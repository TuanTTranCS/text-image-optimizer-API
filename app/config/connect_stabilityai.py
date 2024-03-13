from stability_sdk import client
from os import getenv

STABILITY_CLIENT = None

def connect_StabilityAI(verbose:bool=True):
    """
    Setup authentication to StabilityAI's API client 
    """
    global STABILITY_CLIENT
    if STABILITY_CLIENT is None:
        # Provide StabilityAI's API KEY to connect to OpenAI's API using openai package
        STABILITY_API_KEY = getenv('STABILITY_API_KEY')
         
        # Create connection to OpenAI's API
        STABILITY_CLIENT = client.StabilityInference(
            key=STABILITY_API_KEY, # API Key reference.
    
            verbose=verbose, # Print debug messages.
        )
        
    return STABILITY_CLIENT