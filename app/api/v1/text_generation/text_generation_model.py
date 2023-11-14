from pydantic import BaseModel, Field

# Define your Pydantic models (schemas) here

class TextGenerationInput(BaseModel):
    input_text: str = Field(max_length=300, 
                            title="TextGenerationInput",
                            description="Input text from user, cannot exceed 300 characters")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "input_text": "Salon U is an award-winning salon, established in the year 2002 and known for high-quality beauty, hair, and spa services."
                }
            ]
        }
    }

class TextGenerationOutput(BaseModel):
    generated_texts: list[str] = Field(description="Generated text from the service. Provide multiple option for user")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "generated_texts": [
                        "Salon U - Elevate Your Beauty Experience with Our Award-Winning Hair, Beauty and Spa Services Since 2002",
                        "Explore Salon U - Where Excellence Meets Beauty. Offering Premium Hair, Beauty, and Spa Services for Nearly 20 Years"
                    ]
                }
            ]
        }
    }
