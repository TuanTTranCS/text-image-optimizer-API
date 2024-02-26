from pydantic import BaseModel, Field, model_validator, AnyHttpUrl, FileUrl
# from pydantic_core.core_schema import FieldValidationInfo
from os import getenv
from enum import Enum, auto

from typing import Any, Optional
from typing_extensions import Annotated

import json

from app.utils.logger import get_logger
logger = get_logger(name="app.api.image_optimization.model")

class ImageOptimizationInput(BaseModel):
    image_url: Optional[Annotated[AnyHttpUrl | FileUrl, Field(default=None,
        title="ImageOptimizationInput - Image URL",
        description=f"Input image URL from user/upstream, must be in valid HTTP or fileURL format")]] = None
    image_data: Optional[str] = Field(default=None,
        title="ImageOptimizationInput - Image data base64",
        description=f"Input image data in base64 format from user/upstream")


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
    
        return self 