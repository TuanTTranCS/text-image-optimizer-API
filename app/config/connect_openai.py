from openai import OpenAI
from os import getenv

OPENAI_CLIENT = None
ORGANIZATION_ID = "org-MmAlb4d7l2IzkGO3xcVrYZLV" # Sliike Test from OpenAI's account

def connect_OpenAI():
    global OPENAI_CLIENT
    if OPENAI_CLIENT is None:
        # Provide OpenAI's API KEY to connect to OpenAI's API using openai package
        OPENAI_API_KEY = getenv('OPENAI_API_KEY')

        # Create connection to OpenAI's API
        OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY,
                               organization=ORGANIZATION_ID)
        
    return OPENAI_CLIENT