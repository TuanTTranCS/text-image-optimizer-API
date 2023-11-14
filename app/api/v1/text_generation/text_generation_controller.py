# Define your controller logic here
from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
import json

from app.utils.logger import get_logger
from app.config.connect_openai import connect_OpenAI

logger = get_logger(name="text_optimization")

def generate_text(input_text:str)->list[str]:
    # Call service layer here
    client = connect_OpenAI()
    text_optimizer_model = getenv('TEXT_OPTIMIZER_MODEL') # OpenAI's chat completion model
    n_choices = int(getenv('TEXT_OPTIMIZER_CHOICES')) # number of suggestions provide as output
    text_opt_temperature = float(getenv('TEXT_OPTIMIZER_TEMPERATURE'))
    text_opt_max_tokens = int(getenv('TEXT_OPTIMIZER_MAX_TOKENS'))
    text_opt_prompt = getenv('TEXT_OPTIMIZER_PROMPT').format(n_choices)
    logger.debug(text_opt_prompt)

    # TODO: Get datetime now 
    completion = client.chat.completions.create(
    model=text_optimizer_model,
    messages=[
        {"role": "system", "content": text_opt_prompt},
        {"role": "user", "content": input_text}
    ],
    # n=1,
    temperature=text_opt_temperature,
    max_tokens=text_opt_max_tokens,
    response_format={"type": "json_object"}
    )

    # TODO: Check & response to finish_reason
    generated_texts = json.loads(completion.choices[0].message.content)['messages']
    return generated_texts