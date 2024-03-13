import requests
from base64 import b64decode, b64encode
from io import BytesIO
from PIL import Image
from uuid import uuid4
from os import getenv

images_path = getenv("IMAGES_PATH", "images")

def is_valid_base64_image(image_data_base64:str, size_limit:int=1920):
    """
    Checking for validity of base64 image string, and additional check for image size (in pixel)
    ------------------------
    Return True if the b64 string is from a valid image file (jpg, jpeg, png format) and having
        both the height and width meet the size_limit 
    Reference: https://stackoverflow.com/questions/60186924/python-is-base64-data-a-valid-image  
    """
    
    try:
        image_data_decoded = b64decode(image_data_base64)
        image = Image.open(BytesIO(image_data_decoded))
    except Exception:
        raise Exception('Input string is not a valid Base64 image.')
    # end of check base64 image string
    
    # Checking image format supported
    if image.format.lower() in ["jpg", "jpeg", "png"]:
        
        # Check for image dimension
        width, height = image.size
        if width < size_limit and height < size_limit:
            return True
        else:
            raise Exception(
                f"Image size exceeded, width and height must be less than {size_limit} pixels.")
        # end of checking dimentions
        
    else:
        raise Exception("Image is not valid, only 'Base64' image (jpg, jpeg, png) is valid.")
    # end of checking image format

def convert_image_b64_to_file(image_data_base64:str) -> str:
    """
    Check if the input string is a valid base64 encoded image
    If yes, save the data to a local image file and return the file path in format:
        f"{image_path}/image_{random_uuid4}_{image_extension}"

    """
    converted_image_file = ""
    if is_valid_base64_image(image_data_base64):
        pass
        image_data_decoded = b64decode(image_data_base64)
        image = Image.open(BytesIO(image_data_decoded))
        image_extension = image.format.lower()
        random_id = str(uuid4())
        converted_image_file = f"./{images_path}/image_{random_id}.{image_extension}"
        # converted_img_url = f"http://localhost:8080/static/{image_name}"
        image.save(converted_image_file)
    return converted_image_file

def download_image(image_url:str) -> str:
    """
    Check the input URL links to a valid image file.
    If yes, download the file and return the local file path in format:
        f"{image_path}/image_{random_uuid4}_{image_extension}"

    """
    local_image_file = ""
    image_extension = ""
    image = None
    try:
        image = Image.open(requests.get(image_url, stream=True).raw)
        image_extension = image.format.lower()
    except Exception:
        raise Exception("Invalid image data from input URL.")
    if image_extension != "":
        random_id = str(uuid4())
        local_image_file = f"./{images_path}/image_{random_id}.{image_extension}"
        image.save(local_image_file)
    return local_image_file


def encode_image_b64(image_file:str) -> str:
    encoded_image = ""
    with open(image_file, "rb") as f:
        encoded_image = b64encode(f.read())
    return encoded_image

