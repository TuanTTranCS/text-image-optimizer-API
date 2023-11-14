# Here, include your service layer which interacts with the model to process data
from app.api.v1.text_generation.text_generation_controller import generate_text

def generate_text_service(input_text: str)-> dict[str,list[str]]:
    # This should interact with your text generation logic
    generated_messages = generate_text(input_text)
    return {"generated_texts": generated_messages}  # Mock response
