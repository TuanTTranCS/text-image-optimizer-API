from .image_optimization_controller import upscale_image
from .image_optimization_model import ImageOptimizationInput
# from .text_generation_model import apiSource

def upscale_image_service(input:ImageOptimizationInput)-> dict[str,str]:

    generated_image = upscale_image(input=input)
    return {"image_output": generated_image}  