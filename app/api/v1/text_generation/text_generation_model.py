from pydantic import BaseModel, Field
from os import getenv
from enum import Enum, auto
import json
from datetime import datetime
from dateutil import parser
from time import sleep
from fastapi import status, HTTPException
from openai import APIError, APIConnectionError, RateLimitError, AuthenticationError 
from cohere import CohereError, CohereAPIError, CohereConnectionError
from botocore.exceptions import ClientError

from anthropic_bedrock import HUMAN_PROMPT, AI_PROMPT

from app.utils.logger import get_logger
from app.utils.token_helper import token_counter, token_counter_cohere, token_counter_bedrock
from app.utils.execution_record import execution_time_record
from app.config.connect_openai import connect_OpenAI
from app.config.connect_cohere import connect_Cohere
from app.config.connect_bedrock import connect_Bedrock

# Define your Pydantic models (schemas) here

MAX_CHARS = int(getenv('TEXT_OPTIMIZER_MAX_INPUT_CHARACTERS', 300))
logger = get_logger(name="app.api.text_generation.model")

class TextGenerationInput(BaseModel):
    input_text: str = Field(max_length=MAX_CHARS, 
                            title="TextGenerationInput",
                            description=f"Input text from user, cannot exceed {MAX_CHARS} characters")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "input_text": "Salon U is an award-winning salon, established in the year 2002 and known for high-quality beauty, hair, and spa services."
                }
            ]
        }
    }

class TextGenerationOutput(BaseModel):
    generated_texts: list[str] = Field(description="Generated text from the service. Provide multiple options for user")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "generated_texts": [
                        "Salon U - Elevate Your Beauty Experience with Our Award-Winning Hair, Beauty and Spa Services Since 2002",
                        "Explore Salon U - Where Excellence Meets Beauty. Offering Premium Hair, Beauty, and Spa Services for Nearly 20 Years"
                    ]
                }
            ]
        }
    }

class apiSource(int, Enum):
    cohere = 1
    openai = 2
    anthropic = 3


class OpenAIFinishReason(Enum):
    stop = auto()
    length = auto()
    function_call = auto()
    content_filter = auto()
    null = auto()

class CohereFinishReason(str, Enum):
    COMPLETE = 'COMPLETE'
    ERROR = 'ERROR'
    ERROR_TOXIC = 'ERROR_TOXIC'
    ERROR_LIMIT = 'ERROR_LIMIT'
    USER_CANCEL = 'USER_CANCEL'
    MAX_TOKENS = 'MAX_TOKENS'

class AnthropicFinishReason(str, Enum):
    stop_sequence = 'stop_sequence'
    max_tokens = 'max_tokens'


class _defaultCase(Exception): pass

class TextGenerator:
    def __init__(self, input_text:str, user:str|None=None, api_source:apiSource|None=None):
        self.input_text = input_text
        logger.info(f"User: {user}\nSelected API source: {api_source.name}")
        self.api_source = api_source
        self.n_choices = int(getenv('TEXT_OPTIMIZER_CHOICES', default=2)) # number of suggestions provide as output
        self.max_output_tokens = int(getenv('TEXT_OPTIMIZER_MAX_TOKENS', default=200)) # Control max generate tokens
        try:
            match api_source:
                case apiSource.openai:
                    raise _defaultCase()
                case apiSource.cohere:
                    self.client = connect_Cohere()
                    self.model = getenv('COHERE_TEXT_GEN_MODEL', default='command')
                    self.prompt = getenv('COHERE_TEXT_GEN_PROMPT').format(int(self.max_output_tokens/3))
                    self.messages = [f"Request: \"{self.prompt}\"\nMessage: \"{input_text}\""]
                    self.max_prompt_tokens = int(getenv('COHERE_TEXT_OPTIMIZER_MAX_PROMPT_TOKEN', default=200)) # Internal control on total prompt tokens
                case apiSource.anthropic:
                    self.client = connect_Bedrock()  
                    self.model = getenv('ANTHROPIC_TEXT_GEN_MODEL', default='anthropic.claude-v2:1')     
                    self.prompt = getenv('ANTHROPIC_TEXT_GEN_PROMPT').format(self.n_choices)
                    self.messages = [f"{self.prompt}{HUMAN_PROMPT} {input_text} {AI_PROMPT}{{"]
                    self.max_prompt_tokens = int(getenv('ANTHROPIC_TEXT_OPTIMIZER_MAX_PROMPT_TOKEN', default=200))
        except _defaultCase:
            '''
            Replacement of skipping break for python match:
                https://stackoverflow.com/questions/72273235/how-to-break-the-match-case-but-not-the-while-loop

            '''
            pass
            # api_source = apiSource.openai
            self.client = connect_OpenAI()
            self.model = getenv('OPENAI_TEXT_GEN_MODEL', default='gpt-3.5-turbo-1106') # OpenAI's chat completion model
            self.prompt = getenv('OPENAI_TEXT_GEN_PROMPT').format(self.n_choices) # Prompt message as system guider 
            self.messages = [
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": input_text}
            ]
            self.max_prompt_tokens = int(getenv('OPENAI_TEXT_OPTIMIZER_MAX_PROMPT_TOKEN', default=125)) # Internal control on total prompt tokens
            
        
        self.temperature = float(getenv('ANTHROPIC_TEXT_GEN_TEMPERATURE', default=.8)) if api_source == apiSource.anthropic else \
            float(getenv('TEXT_OPTIMIZER_TEMPERATURE', default=1.3)) # Level of creativeness of the response
        
        
        logger.info("Input messages:")
        logger.info(self.messages)
        
        self.user = user
        
    def calculate_prompt_tokens_count(self)->int:
        """
        Calculate the total tokens submitted to OpenAI's chat completion API based on the prompt message, input user message and the model used
        Using OpenAI's tiktoken module to calculate the tokens for prompt message and user message
        --------------------- 
        Return prompt_tokens_count + user_tokens_count + 11

        """
        if self.api_source == apiSource.openai:
            prompt_tokens_count = token_counter(self.prompt, self.model)
            user_tokens_count = token_counter(self.input_text, self.model)
            return prompt_tokens_count + user_tokens_count + 11
        elif self.api_source == apiSource.cohere:
            return token_counter_cohere(self.messages[0], self.model)
        elif self.api_source == apiSource.anthropic:
            return token_counter_bedrock(string=self.messages[0], 
                client=self.client, 
                model_id=self.model)
        else: 
            return -1
    

    def send_text_generation_request(self):
        """
        Generic method to call the proper API endpoint depending on the API source
        
        """
        try:
            if self.api_source == apiSource.cohere:
                return self.send_cohere_request()
            elif self.api_source == apiSource.openai:
                return self.send_openai_request()
            elif self.api_source == apiSource.anthropic:
                return self.send_anthropic_bedrock_request()
        except Exception as e: # Catch all generic exeption that does not related to any 3rd party service
            response_message = "An generic exception occurred. Please contact administrator for the issue." 
            logger.info(f"{response_message} Error: {e}") 
            raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, detail=response_message)


    def send_openai_request(self):
        """
        Create request and send to OpenAI's chat completion API endpoint
        References: 
            https://platform.openai.com/docs/guides/text-generation/chat-completions-api
            https://platform.openai.com/docs/api-reference/completions

        Returns the response from the sent request (ChatCompletion object)
                       
        """
        
        try:
            start_time = datetime.now()
            completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            # n=1,
            temperature=self.temperature,
            max_tokens=self.max_output_tokens,
            user=self.user if self.user is not None else 'user123',
            response_format={"type": "json_object"}
            )
            finish_time = datetime.now()
            execution_time_ms = (finish_time - start_time).total_seconds() * 1000

            logger.info("OpenAI's Response:")
            logger.info(completion)
            # Retrieve finish reason for handling response from API call 
            
            finish_reason = completion.choices[0].finish_reason          

            # Retrieve tokens usage and other info from OpenAI's response for 
            # future's DB record & analysis purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
            completion_tokens_count = completion.usage.completion_tokens # generated message's token count
            prompt_tokens_count = completion.usage.prompt_tokens # total input + prompt token count
            created_timestamp = completion.created # Unix timestamp
            db_record = {'created_timestamp': datetime.fromtimestamp(created_timestamp), 
                         'task': "text_optimization",
                         'api_source': self.api_source,
                         'model': self.model,
                         'user': self.user,
                         'input_messages': self.messages,
                         'execution_time_ms': execution_time_ms,
                         'prompt_tokens_count': prompt_tokens_count, 'completion_tokens_count': completion_tokens_count,
                         'generated_texts': completion.choices[0].message.content,
                         'finish_reason': [finish_reason]}
            logger.info(db_record)
            execution_time_record(db_record)

            if finish_reason == OpenAIFinishReason.stop.name:
                generated_texts = json.loads(completion.choices[0].message.content)['messages']
                if len(generated_texts) == self.n_choices:
                    return generated_texts
                else:
                    pass
            if finish_reason == OpenAIFinishReason.length.name:
                response_message = f"Partial output retrieved ({status.HTTP_422_UNPROCESSABLE_ENTITY}): " +\
                    "Request was successfully sent to OpenAI but the output response was incomplete due to" +\
                    "max output tokens control. Will auto retry again if within retry limit."
                logger.info(response_message)
                return None
                
            if finish_reason == OpenAIFinishReason.content_filter.name:
                response_message = f"Partial output retrieved ({status.HTTP_400_BAD_REQUEST}): " +\
                    "Request was successfully sent to OpenAI but the user message was flagged due to" +\
                    "their content filters. Please retry with a proper message."
                logger.info(response_message)
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_message)
            
            if finish_reason == OpenAIFinishReason.null.name:
                # Not sure what to do yet
                pass

        except APIError as e:
            #Handle API error here, e.g. retry or log
            logger.info(f"OpenAI API returned an API Error: {e}")
            if '401' in e.message:
                response_message = f"OpenAI API authentication error. Please ask admin / developer to verify the provided OpenAI's API key."
                raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=response_message)
            # Other error than 401, wait for 3 seconds and retry in next loop
            sleep(3)
            return None

        except APIConnectionError as e:
            #Handle connection error here
            logger.info(f"Failed to connect to OpenAI API: {e}")
            response_message = f"Failed Dependency ({status.HTTP_424_FAILED_DEPENDENCY}): " + \
                "Failed to conenct to OpenAI API. Please check with web admin / developer."
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=response_message)
        except RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            logger.info(f"OpenAI API request exceeded rate limit: {e}")
            response_message = f"Failed Dependency ({status.HTTP_424_FAILED_DEPENDENCY}): " + \
                "OpenAI API request exceeded rate limit. Please wait for a few seconds and retry request again."
            sleep(3)
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=response_message)
        except AuthenticationError as e:
            logger.info(f"OpenAI API client cannot be authenticated: {e}")
            response_message = f"Failed Dependency ({status.HTTP_424_FAILED_DEPENDENCY}): " + \
                "Failed to authenticate OpenAI API. Please contact web admin / developer."
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=response_message)
        
    
    def send_cohere_request(self):
        """
        Create request and send to Cohere's text generation API using Cohere python SDK
        References:
            https://cohere-sdk.readthedocs.io/en/latest/cohere.html#cohere.client.Client.generate
            https://cohere-sdk.readthedocs.io/en/latest/cohere.html#cohere.error.CohereError 
        Returns the response from the sent request (Generations object)

        """
        try:
            start_time = datetime.now()
            cohere_generate_response = self.client.generate(
                model=self.model,
                prompt=self.messages[0],
                num_generations=self.n_choices,
                max_tokens=self.max_output_tokens,
                temperature=self.temperature,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE')
            
            finish_time = datetime.now()
            execution_time_ms = (finish_time - start_time).total_seconds() * 1000

            logger.info("Cohere's Response:")
            logger.info(cohere_generate_response)
            
            finish_reasons = [response.finish_reason for response in cohere_generate_response.generations]

            # Retrieve tokens usage and other info from OpenAI's response for 
            # future's DB record & analysis purpose     
            completion_tokens_count = cohere_generate_response.meta['billed_units']['output_tokens'] # generated message's token count
            prompt_tokens_count = cohere_generate_response.meta['billed_units']['input_tokens'] # total input + prompt token count
            created_timestamp = start_time
            db_record = {'created_timestamp': created_timestamp, 
                         'task': "text_optimization",
                         'api_source': self.api_source,
                         'model': self.model,
                         'user': self.user,
                         'input_messages': self.messages,
                         'execution_time_ms': execution_time_ms,
                         'prompt_tokens_count': prompt_tokens_count, 'completion_tokens_count': completion_tokens_count,
                         'generated_texts': [generation.text for generation in cohere_generate_response.generations],
                         'finish_reason': finish_reasons}
            logger.info(db_record)
            execution_time_record(db_record)

            if all([finish_reason == CohereFinishReason.COMPLETE for finish_reason in finish_reasons]):
                return [response.text.split("```")[1].replace('\n','') for response in cohere_generate_response.generations \
                        if response.text.count("```")==2]
            elif any([finish_reason == CohereFinishReason.ERROR for finish_reason in finish_reasons]):
                pass
                logger.info("An error occured during text generation for one of the responses. Will retry again if still within retry limit.")
                return None
            elif any([finish_reason == CohereFinishReason.ERROR_LIMIT for finish_reason in finish_reasons]):
                pass
                if len([finish_reason == CohereFinishReason.ERROR_LIMIT for finish_reason in finish_reasons if finish_reason == CohereFinishReason.ERROR_LIMIT]) == 1:
                    logger.info("An error occured during text generation for one of the responses: the context is too big to generate (exceeded the model's context limit)." + \
                                "Will return any COMPLETE response remaining.")
                    return [response.text.split("```")[1].replace('\n','') for response in cohere_generate_response.generations \
                        if all([response.text.count("```")==2, response.finish_reason == CohereFinishReason.COMPLETE])]
                else:
                    logger.info("An error occured during text generation for all of the responses: the context is too big to generate (exceeded the model's context limit)." + \
                                "Will retry again if still within retry limit.")
                    return None
            elif any([finish_reason == CohereFinishReason.ERROR_TOXIC for finish_reason in finish_reasons]):
                response_message = "An error occured during text generation for one of the responses: text generation is halted due to toxic output." + \
                             " Please retry your input text with a proper message content." 
                logger.info(response_message)
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_message)
            elif any([finish_reason == CohereFinishReason.USER_CANCEL for finish_reason in finish_reasons]):  
                response_message = "User has cancelled the text generation request." 
                logger.info(response_message) 
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_message)
            
        except CohereAPIError as e:
            response_message = f"Cohere API error. Details: {e}. Will auto retry again if still within retry limit."
            logger.info(response_message)
            # Wait for 3 seconds and retry in next loop
            sleep(3)
            return None
        except CohereError as e:
            
            response_message = f"Cohere API generic error: {e}. Will auto retry again if still within retry limit."
            logger.info(response_message)
            # Wait for 3 seconds and retry in next loop
            sleep(3)
            return None
        except CohereConnectionError as e:
            logger.info(f"Cohere API connection error: the SDK cannot reach the API server. Details: {e}")
            sleep(3)
            return None
            
        return cohere_generate_response
    
    def send_anthropic_bedrock_request(self):
        """
        Create request and send to Anthropic's text generation API using AWS Bedrock python SDK (boto3)
        References:
            https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html 
            https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html 
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/invoke_model.html#
            https://docs.anthropic.com/claude/reference/complete_post

        Returns the Response object from the bedrock runtime client ()

        """
        try:
            
            request_body = json.dumps({"prompt": self.messages[0],
                   "max_tokens_to_sample": self.max_output_tokens,
                   "temperature": self.temperature,
                   "stop_sequences": ["}}"]
                   })
            accept = "application/json"
            contentType = "application/json"
            start_time = datetime.now()
            response = self.client.invoke_model(
                body=request_body, modelId=self.model, 
                accept=accept, 
                contentType=contentType
              
            )

            finish_time = datetime.now()
            execution_time_ms = (finish_time - start_time).total_seconds() * 1000
            
            logger.info("Anthropic's Response:")
            logger.info(response)
            response_body = json.loads(response.get("body").read())

            finish_reason = response_body['stop_reason']
            # Retrieve tokens usage and other info from OpenAI's response for 
            # future's DB record & analysis purpose     

            completion_tokens_count = int(response['ResponseMetadata']['HTTPHeaders']['x-amzn-bedrock-output-token-count']) # generated message's token count
            prompt_tokens_count = int(response['ResponseMetadata']['HTTPHeaders']['x-amzn-bedrock-input-token-count']) # total input + prompt token count
            created_timestamp = parser.parse(response['ResponseMetadata']['HTTPHeaders']['date'])
            db_record = {'created_timestamp': created_timestamp, 
                         'task': "text_optimization",
                         'api_source': self.api_source,
                         'model': self.model,
                         'user': self.user,
                         'input_messages': self.messages,
                         'execution_time_ms': execution_time_ms,
                         'prompt_tokens_count': prompt_tokens_count, 'completion_tokens_count': completion_tokens_count,
                         'generated_texts': [response_body['completion']],
                         'finish_reason': [finish_reason]}
            
            execution_time_record(db_record)
            logger.info(db_record)

            if finish_reason == AnthropicFinishReason.stop_sequence:
                generated_texts = json.loads('{' + response_body['completion'])['messages']
                if len(generated_texts) == self.n_choices:
                    return generated_texts
                else:
                    response_message = "Request was successfully sent to Anthropic Bedrock but the output response was incomplete due to" +\
                    f"not meeting the expected number of {self.n_choices} choice(s). Will auto retry again if within retry limit."
                    logger.info(response_message)
                    return None
            elif finish_reason == AnthropicFinishReason.max_tokens:
                logger.info("An error occured during text generation: the generated response exceeded 'max_tokens_to_sample' or the model's context limit)." + \
                    "Will retry again if still within retry limit.")
                return None

        except ClientError as error:
            # AccessDeniedException, ResourceNotFoundException, ThrottlingException, \
            # ModelTimeoutException, InternalServerException, ValidationException, ModelNotReadyException, ServiceQuotaExceededException, \
            # ModelErrorException
            if error.response['Error']['Code'] == 'AccessDeniedException':
                response_message = f"\x1b[41m{error.response['Error']['Message']}\
                \nTo troubeshoot this issue please refer to the following resources.\
                 \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                 \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n"
                logger.info(response_message)
                user_response = "Access Denied from Anthropic Bedrock, please contact administrator."
                raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=user_response)
            elif error.response['Error']['Code'] == 'ResourceNotFoundException':
                response_message = f"The specified resource ARN was not found. Check the ARN and try your request again. Detailed error: {error}"
                logger.info(response_message)
                user_response = "ResourceNotFoundException raised by Anthropic Bedrock, please contact administrator."
                raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=user_response)
            elif error.response in ['ServiceQuotaExceededException', 'ThrottlingException']:
                response_message = f"Failed Dependency ({status.HTTP_424_FAILED_DEPENDENCY}): " + \
                "Anthropic bedrock request exceeded rate limit or service quota. Please wait for a few seconds and retry request again."
                logger.info(response_message + f"Detailed error: {error}")
                sleep(3)
                raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=response_message)
            elif error.response['Error']['Code'] == 'ValidationException':
                response_message = "Input validation failed from Anthropic Bedrock. Please contact administrator to check for request parameters."
                logger.info(response_message + f"Detailed error: {error}")
                raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=response_message)
                
            else:
                logger.info(f"Anthropic Bedrock client cannot invoke due to an error. Will auto retry again if within retry limit. Details: {error}")
                sleep(3)
                return None
        
        return response
        