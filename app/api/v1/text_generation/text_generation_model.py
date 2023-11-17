from pydantic import BaseModel, Field
from os import getenv
from enum import Enum, auto

from app.utils.logger import get_logger
from app.utils.token_helper import token_counter
from app.config.connect_openai import connect_OpenAI

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

class OpenAIFinishReason(Enum):
    stop = auto()
    length = auto()
    function_call = auto()
    content_filter = auto()
    null = auto()

class TextGenerator:
    def __init__(self, input_text:str, user:str|None=None):
        self.input_text = input_text
        self.openai_client = connect_OpenAI()
        self.openai_model = getenv('TEXT_OPTIMIZER_MODEL', default='gpt-3.5-turbo-1106') # OpenAI's chat completion model
        self.n_choices = int(getenv('TEXT_OPTIMIZER_CHOICES', default=2)) # number of suggestions provide as output
        self.temperature = float(getenv('TEXT_OPTIMIZER_TEMPERATURE', default=1.3)) # Level of creativeness of the response
        self.max_output_tokens = int(getenv('TEXT_OPTIMIZER_MAX_TOKENS', default=200)) # Control max generate tokens
        self.prompt = getenv('TEXT_OPTIMIZER_PROMPT').format(self.n_choices) # Prompt message as system guider 
        logger.debug(self.prompt)
        self.max_prompt_tokens = int(getenv('TEXT_OPTIMIZER_MAX_PROMPT_TOKEN', default=125)) # Internal control on total prompt tokens
        self.user = user
        self.messages = [
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": input_text}
                ]

    def calculate_prompt_tokens_count(self)->int:
        """
        Calculate the total tokens submitted to OpenAI's chat completion API based on the prompt message, input user message and the model used
        Using OpenAI's tiktoken module to calculate the tokens for prompt message and user message
        --------------------- 
        Return prompt_tokens_count + user_tokens_count + 11

        """
        prompt_tokens_count = token_counter(self.prompt, self.openai_model)
        user_tokens_count = token_counter(self.input_text, self.openai_model)
        return prompt_tokens_count + user_tokens_count + 11
    
    def send_openai_request(self):
        """
        Create request and send to OpenAI's chat completion API endpoint
        References: 
            https://platform.openai.com/docs/guides/text-generation/chat-completions-api
            https://platform.openai.com/docs/api-reference/completions
                       
        """
        completion = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=self.messages,
            # n=1,
            temperature=self.temperature,
            max_tokens=self.max_output_tokens,
            user=self.user if self.user is not None else 'user123',
            response_format={"type": "json_object"}
            )
        return completion