# Define your controller logic here
from os import getenv
import json
from time import sleep
from fastapi import status, HTTPException
from openai import APIError, APIConnectionError, RateLimitError, AuthenticationError 

from app.utils.logger import get_logger
from app.utils.sentence_checker import SentenceChecker
from app.config.connect_openai import connect_OpenAI
from .text_generation_model import OpenAIFinishReason, TextGenerator

logger = get_logger(name="app.api.text_generation.controller")

def generate_text(input_text:str, user:str|None=None)->list[str]:
    """
    Control flow to validate user input_text and return appropriate response
    user: placeholder for hashed userId / username / email address for future tracking
    """
    # Call service layer here

    sentence_check = SentenceChecker()
    if sentence_check.is_sentence_meaningless(input_text):
        response_message = f"Validation error ({status.HTTP_422_UNPROCESSABLE_ENTITY}): " + \
            "Client's input text format is valid but does not have any meaningful English word."
        logger.info(response_message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_message)

    text_generator = TextGenerator(input_text, user) # Create and initialize text generator instance

    # Check if the input to be submitted exceed the controlled number of tokens or not
    input_prompt_tokens_count = text_generator.calculate_prompt_tokens_count()
    # TODO: Get datetime now 
    max_retry = int(getenv('TEXT_OPTIMIZER_MAX_RETRY', default=2))
    if input_prompt_tokens_count <= text_generator.max_prompt_tokens:
        for _ in range(0, max_retry + 1):
            retry_count = 0
            try:
                completion = text_generator.send_openai_request()
                logger.info(completion)
                # Retrieve finish reason for handling response from API call 
                finish_reason = completion.choices[0].finish_reason          

                # Retrieve tokens usage and other info from OpenAI's response for 
                # future's DB record & analysis purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
                completion_tokens_count = completion.usage.completion_tokens # generated message's token count
                prompt_tokens_count = completion.usage.prompt_tokens # total input + prompt token count
                created_timestamp = completion.created # Unix timestamp

            
                # TODO: Check & response to finish_reason
                if finish_reason == OpenAIFinishReason.stop.name:
                    generated_texts = json.loads(completion.choices[0].message.content)['messages']
                    return generated_texts
                if finish_reason == OpenAIFinishReason.length.name:
                    response_message = f"Partial output retrieved ({status.HTTP_422_UNPROCESSABLE_ENTITY}): " +\
                        "Request was successfully sent to OpenAI but the output response was incomplete due to" +\
                        "max output tokens control."
                    logger.info(response_message)
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_message)
                    
                if finish_reason == OpenAIFinishReason.content_filter.name:
                    response_message = f"Partial output retrieved ({status.HTTP_400_BAD_REQUEST}): " +\
                        "Request was successfully sent to OpenAI but the user message was flagged due to" +\
                        "their content filters."
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
                continue
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
            retry_count += 1
            logger.info(f"Retry attemp: {retry_count}/{max_retry}")

        if retry_count == max_retry:
            logger.info(f"Too many request ({status.HTTP_429_TOO_MANY_REQUESTS}): Exceeded max retry attempts ({retry_count}/{max_retry})")
            response_message = f"Too many requests ({status.HTTP_429_TOO_MANY_REQUESTS}): Exceeded max internal retry attempts. Please try again later."            

    else:
        response_message = f"Validation error ({status.HTTP_422_UNPROCESSABLE_ENTITY}): " +\
            "Client's input text format is valid but total number of prompt tokens exceeded " +\
            "control limit. Please try to reduce the number of words in the input."
        logger.info(response_message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_message)
        