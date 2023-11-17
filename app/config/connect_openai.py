from openai import OpenAI
from os import getenv

OPENAI_CLIENT = None

def connect_OpenAI():
    """
    Setup authentication to OpenAI's API client 
    """
    global OPENAI_CLIENT
    if OPENAI_CLIENT is None:
        # Provide OpenAI's API KEY to connect to OpenAI's API using openai package
        OPENAI_API_KEY = getenv('OPENAI_API_KEY')
        ORGANIZATION_ID = getenv('OPENAI_ORGANIZATION_ID') # Organization ID from OpenAI's account, in Settings 
        # Create connection to OpenAI's API
        OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY,
                               organization=ORGANIZATION_ID)
        
    return OPENAI_CLIENT