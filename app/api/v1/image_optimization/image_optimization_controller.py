# Define your controller logic here
from os import getenv
import json

from fastapi import status, HTTPException


from app.utils.logger import get_logger
from app.utils.image_utils import convert_image_b64_to_file, is_valid_base64_image
from .image_optimization_model import ImageOptimizationInput, ImageOptimizer

logger = get_logger(name="app.api.image_optimization.controller")

def upscale_image(input:ImageOptimizationInput) -> str:
    """
    Receive image input (URL/ Base 64 encoded string) from client
    Generate upscaled image in encoded Base64 string format
    """
    generated_image_b64 = ""
    image_optimizer = ImageOptimizer(input)
    generated_image_b64 = image_optimizer.send_image_upscale_request()
    return generated_image_b64