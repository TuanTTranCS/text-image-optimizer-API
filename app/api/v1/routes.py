from fastapi import APIRouter
from .text_generation.text_generation_route import router as text_generation_router
from .image_optimization.image_optimization_route import router as image_optimization_router

api_router = APIRouter()

api_router.include_router(text_generation_router, prefix="/text-generation", tags=["Text Generation"])
api_router.include_router(image_optimization_router, prefix="/image-optimization", tags=["Image Optimization"])
