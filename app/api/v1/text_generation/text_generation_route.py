from typing import Annotated
from fastapi import APIRouter, Response, Query, Body
from .text_generation_model import TextGenerationInput, TextGenerationOutput, apiSource
from .text_generation_service import generate_text_service

router = APIRouter()

@router.post("/generate", response_model=TextGenerationOutput)
async def generate_text(input: Annotated[TextGenerationInput, Body()], 
                        user: Annotated[str|None, Query(title="User Id / User name",
                                                        description="User Id for usage tracking purpose",
                                                        max_length=15)] = None, 
                        api_source: Annotated[apiSource|None, Query(title="API Source Id",
                                                                    description="Internal API source ID (Id of the model company to use)")] = None
                        ):
    return generate_text_service(input.input_text, user, api_source)
