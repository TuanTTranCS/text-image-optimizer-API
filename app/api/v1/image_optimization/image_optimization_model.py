from pydantic import BaseModel, Field, model_validator, AnyHttpUrl, FileUrl
# from pydantic_core.core_schema import FieldValidationInfo
from os import getenv
from enum import Enum, auto
from PIL import Image
from typing import Any, Optional
from typing_extensions import Annotated

from fastapi import status, HTTPException

from app.config.connect_claidai import connect_ClaidAI 
from app.utils.image_utils import is_valid_base64_image, convert_image_b64_to_file, download_image, encode_image_b64
# import json

from app.utils.logger import get_logger
logger = get_logger(name="app.api.image_optimization.model")

static_images_path = "/static"

class ImageOptimizationInput(BaseModel):
    image_url: Optional[Annotated[AnyHttpUrl | FileUrl, Field(default=None,
        title="ImageOptimizationInput - Image URL",
        description=f"Input image URL from user/upstream, must be in valid HTTP or fileURL format",
        examples=["https://i0.wp.com/www.agilenative.com/wp-content/uploads/2017/01/001-Agile-Hello-World.png"])]] = None
    image_data: Optional[str] = Field(default=None,
        title="ImageOptimizationInput - Image data base64",
        description=f"Input image data in base64 format from user/upstream",
        examples=["SGVyZSBpcyBhIEJhc2U2NCBzdHJpbmcu"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "image_url": "https://i0.wp.com/www.agilenative.com/wp-content/uploads/2017/01/001-Agile-Hello-World.png"
                },
                {
                    "image_data": "SGVyZSBpcyBhIEJhc2U2NCBzdHJpbmcu"
                }
            ]
        }
    }

    @model_validator(mode="after")
    # @classmethod
    def check_url_or_data(self) -> 'ImageOptimizationInput':
        co_exist_statement = "Input image can only be passed through either 'image_url' or 'image_data'" + \
            ", both fields cannot be existed at the same time."
        none_field_exist_statement = "Missing image input: input image must be either passed through " + \
            "image's URL (via 'image_url' field) or encoded Base64 data (via 'image_data' field)."

        url = self.image_url
        data = self.image_data
        if url is not None and data is not None:
            raise ValueError(co_exist_statement)
        if url is None and data is None:
            raise ValueError(none_field_exist_statement)
        if data is not None:
            if is_valid_base64_image(data):
                pass
    
        return self 
    
class ImageOptimizationOutput(BaseModel):
   image_output: str = Field(description="Generated image in encoded Base64 format")

   model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "image_output": 
                        "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAAXNSR0IArs4c6QAAAARnQU1BAACx" + \
                        "jwv8YQUAAAAJcEhZcwAAGdYAABnWARjRyu0AAAArSURBVBhXY3gro4IVESHBAAYILlz0/ycQgssRk" + \
                        "oDIwUVBXDgLDeGQkFEBABnNROlgDjt2AAAAAElFTkSuQmCC"
                    
                }
            ]
        }
    }
   

class _defaultCase(Exception): pass

class ImageOptimizer:
    def __init__(self, input_image: ImageOptimizationInput):
        self.input_image_path = None
        try:
                
            if input_image.image_data is not None:
                self.input_image_path = convert_image_b64_to_file(input_image.image_data)
            else:
                self.input_image_path = download_image(input_image.image_url)
            if self.input_image_path is not None:
                logging_message = f"Input image successfully saved to '{self.input_image_path}'."
                logger.info(logging_message)
                self.client = connect_ClaidAI()
                logger.info("CLAID.AI client initiated.")
        except Exception as e:
            response_message = "Invalid input image data / URL."
            logger.info(f"{response_message} Error: {e}") 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response_message)
        

    def send_image_upscale_request(self):
        try:
            image = Image.open(open(self.input_image_path, 'rb'))
            image_format = 'jpeg' if image.format.lower() in ['jpg', 'jpeg'] else 'png'
            response = self.client.upscale(self.input_image_path, format=image_format)

            if response.status_code != 200:
                response_code = response.status_code
                logging_message = f"Status code: {response_code}. " + "Response: " + str(response.text)
                response_message = "Error while sending image upscale request. Please contact administrator for the issue."
                logger.info(logging_message)
                raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=response_message)

            generated_image_url = response.json()['data']['output']['tmp_url']
            generated_image_file = download_image(generated_image_url)

            logging_message = f"Upscaled image successfully saved to file '{generated_image_file}'"
            logger.info(logging_message)

            encoded_image = encode_image_b64(generated_image_file)
            return encoded_image

        except Exception as e:
            response_message = "An generic exception occurred. Please contact administrator for the issue." 
            logger.info(f"{response_message} Error: {e}") 
            raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, detail=response_message)
   
        return
        