from os import getenv
from pathlib import Path
import requests
import json

CLAIDAI_CLIENT = None

CLAID_API_HOST = getenv("CLAID_API_HOST", "https://api.claid.ai")

class ClaidAPIClient:
    def __init__(self, api_key):
        self.base_url = f"{CLAID_API_HOST}/v1-beta1"
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def upscale(self, image_path, format:str='png'):
        '''
        Upscale image using default settings from CLAID.AI's API reference:
            Upload edit: https://docs.claid.ai/image-editing-api/upload-api-reference
            Upscale / enhance: https://docs.claid.ai/image-editing-api/image-operations/restorations


        '''
        endpoint = "/image/edit/upload"
        url = f"{self.base_url}{endpoint}"
        output_format = {
                        "type": "png",
                        "compression": "optimal"
                        }
        if format == 'jpeg':
            output_format = {
                        "type": "jpeg",
                        "quality": 85
                        # , "progressive": "true"
                        }
        payload = {
                "operations": {
                    "restorations": {
                        "decompress": "auto",
                        "upscale": "smart_enhance"
                    },
                    "resizing": {
                        "width": "200%",
                        "height": "200%",
                        "fit": "bounds"
                    }
                },
                "output": {
                    "format": output_format
                }
            }

        # Read the image file
        with open(image_path, "rb") as image_file:
            files = {"file": (Path(image_path).name, image_file, "form-data"),
                     "data": (None, json.dumps(payload), "application/json")}

            # Define the JSON data for the request
            

            # Make the POST request
            response = requests.post(url, 
                                     headers=self.headers, 
                                     files=files 
                                     )

            if response.status_code == 200:
                return response
            else:
                return f"Error: {response.status_code} - {response.text}"

def connect_ClaidAI():
    global CLAIDAI_CLIENT
    if CLAIDAI_CLIENT is None:
        CLAID_API_KEY = getenv("CLAID_API_KEY")
        
        CLAIDAI_CLIENT = ClaidAPIClient(api_key=CLAID_API_KEY)
        
    return CLAIDAI_CLIENT