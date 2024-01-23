# Define your controller logic here
from os import getenv
import json

from fastapi import status, HTTPException


from app.utils.logger import get_logger
from app.utils.sentence_checker import SentenceChecker
from app.config.connect_openai import connect_OpenAI
from .text_generation_model import TextGenerator, apiSource

logger = get_logger(name="app.api.text_generation.controller")

def generate_text(input_text:str, user:str|None=None, api_source:apiSource|None=None)->list[str]:
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

    text_generator = TextGenerator(input_text, user=user, api_source=api_source) # Create and initialize text generator instance

    # Check if the input to be submitted exceed the controlled number of tokens or not
    input_prompt_tokens_count = text_generator.calculate_prompt_tokens_count()
    # TODO: Get datetime now 
    max_retry = int(getenv('TEXT_OPTIMIZER_MAX_RETRY', default=2))
    if input_prompt_tokens_count <= text_generator.max_prompt_tokens:
        for _ in range(0, max_retry + 1):
            retry_count = 0
            response = text_generator.send_text_generation_request()
            if response is not None:
                return response
            else:  
                retry_count += 1
                logger.info(f"Retry attemp: {retry_count}/{max_retry}")
                if retry_count == max_retry:
                    logger.info(f"Too many request ({status.HTTP_429_TOO_MANY_REQUESTS}): Exceeded max retry attempts ({retry_count}/{max_retry})")
                    response_message = f"Too many requests ({status.HTTP_429_TOO_MANY_REQUESTS}): Exceeded max internal retry attempts. Please try again later."            
                else:
                    continue

    else:
        response_message = f"Validation error ({status.HTTP_422_UNPROCESSABLE_ENTITY}): " +\
            "Client's input text format is valid but total number of prompt tokens exceeded " +\
            "control limit. Please try to reduce the number of words in the input."
        logger.info(response_message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_message)
        