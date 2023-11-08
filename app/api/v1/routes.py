from fastapi import APIRouter
from .text_generation.text_generation_route import router as text_generation_router

api_router = APIRouter()

api_router.include_router(text_generation_router, prefix="/text-generation", tags=["Text Generation"])

