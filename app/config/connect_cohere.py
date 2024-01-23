from cohere import Client
from os import getenv

COHERE_CLIENT = None

def connect_Cohere():
    """
    Setup authentication to Cohere's API client 
    """
    global COHERE_CLIENT
    if COHERE_CLIENT is None:
        # Provide Cohere's API KEY to connect to Cohere's API using cohere  package
        COHERE_API_KEY = getenv('COHERE_API_KEY')
        #ORGANIZATION_ID = getenv('OPENAI_ORGANIZATION_ID') # Organization ID from OpenAI's account, in Settings 
        COHERE_CLIENT_NAME = getenv('COHERE_CLIENT_NAME')
        # Create connection to OpenAI's API
        COHERE_CLIENT = Client(api_key=COHERE_API_KEY,
                                client_name=COHERE_CLIENT_NAME
                               )
        
    return COHERE_CLIENT