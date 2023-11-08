from pydantic import BaseModel

# Define your Pydantic models (schemas) here

class TextGenerationInput(BaseModel):
    input_text: str

class TextGenerationOutput(BaseModel):
    generated_text: str
