from typing import Annotated
from fastapi import APIRouter, Query, Body
from .image_optimization_model import ImageOptimizationInput, ImageOptimizationOutput
from .image_optimization_service import upscale_image_service

router = APIRouter()

@router.post("/upscale", response_model=ImageOptimizationOutput)
async def upscale_image(
        input: Annotated[ImageOptimizationInput, 
                         Body(
                             openapi_examples={
                "image_url": {
                    "summary": "An example using image URL",
                    "description": "Input image mode using **image URL**",
                    "value": {
                        "image_url": "https://docs.gimp.org/en/images/filters/examples/noise/taj-rgb-noise.jpg"
                    }
                },
                "image_data": {"summary": "An example using Base 64 string",
                               "description": "Input image mode using **image Base64 encoded string**",
                               "value": {
                                   "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAGdYAABnWARjRyu0AAAArSURBVBhXY3gro4IVESHBAAYILlz0/ycQgssRkoDIwUVBXDgLDeGQkFEBABnNROlgDjt2AAAAAElFTkSuQmCC"
                               }
                               }
                             }
                             
                         )]
                        ):
    return upscale_image_service(input)