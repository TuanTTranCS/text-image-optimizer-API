# Source: https://stackoverflow.com/questions/75804599/openai-api-how-do-i-count-tokens-before-i-send-an-api-request

import tiktoken
from langchain.llms import Bedrock
# from botocore.client import 
from app.config.connect_cohere import connect_Cohere

def encoding_getter(encoding_type: str):
    """
    Returns the appropriate encoding based on the given encoding type (either an encoding string or a model name).
    """
    if "k_base" in encoding_type:
        return tiktoken.get_encoding(encoding_type)
    else:
        return tiktoken.encoding_for_model(encoding_type)

def tokenizer(string: str, encoding_type: str) -> list:
    """
    Returns the tokens in a text string using the specified encoding.
    """
    encoding = encoding_getter(encoding_type)
    tokens = encoding.encode(string)
    return tokens

def token_counter(string: str, encoding_type: str) -> int:
    """
    Returns the number of tokens in a text string using the specified encoding.
    """
    num_tokens = len(tokenizer(string, encoding_type))
    return num_tokens

def token_counter_cohere(string:str, model:str) -> int:
    co = connect_Cohere()
    response = co.tokenize(string, model=model)
    return len(response.tokens)

def token_counter_bedrock(string:str, client, model_id:str):
    """
    References: https://github.com/anthropics/anthropic-bedrock-python/blob/main/src/anthropic_bedrock/_tokenizers.py
        count_tokens from https://github.com/anthropics/anthropic-bedrock-python/blob/main/src/anthropic_bedrock/_client.py 
        https://how.wtf/how-to-count-amazon-bedrock-anthropic-tokens-with-langchain.html 
    """
    pass
    llm = Bedrock(client=client, model_id=model_id)
    return llm.get_num_tokens(string)
