from fastapi import APIRouter, Response
from .text_generation_model import TextGenerationInput, TextGenerationOutput
from .text_generation_service import generate_text_service

router = APIRouter()

@router.post("/generate", response_model=TextGenerationOutput)
async def generate_text(input: TextGenerationInput):
    return generate_text_service(input.input_text)
