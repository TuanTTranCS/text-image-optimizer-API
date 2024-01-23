# Here, include your service layer which interacts with the model to process data
from .text_generation_controller import generate_text
from .text_generation_model import apiSource

def generate_text_service(input_text: str, user:str|None=None, api_source:apiSource|None=None)-> dict[str,list[str]]:
    # This should interact with your text generation logic
    if api_source is None: # Define default API source if not specified
        generated_messages = generate_text(input_text, user=user, api_source=apiSource.openai)
    else:    
        generated_messages = generate_text(input_text, user=user, api_source=api_source)
    return {"generated_texts": generated_messages}  # Mock response
