from fastapi import FastAPI
from dotenv import load_dotenv
import os
load_dotenv(override=True)

from contextlib import asynccontextmanager
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.api.v1.routes import api_router
from app.config.connect_db import get_database
from app.config.connect_openai import connect_OpenAI
from app.middleware.api_key_auth import api_key_auth
from app.middleware.error_handler import (
    http_exception_handler,
    request_validation_exception_handler,
    validation_exception_handler
)

images_path = os.getenv("IMAGES_PATH", "images")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Define the startup and shutdown actions of the app
    """
    # Before the app start:

    app.db = get_database() # Load database connection

    # Create static files folder
    
    if not (os.path.exists(images_path)):
        os.makedirs(images_path)
        print(f"'{images_path}' path created.")
    
    yield
    
    # After the app finish (before shutdown)
    app.db.client.close()

tags_metadata = [
    {
        "name": "Text Generation",
        "description": "Optimize user's input text",
    },
    {
        "name": "Image Optimization",
        "description": "Optimize user's input image (upscale, enhance, edit, etc..)",
        # "externalDocs": {
        #     "description": "Items external docs",
        #     "url": "https://fastapi.tiangolo.com/",
        # },
    },
]

app = FastAPI(lifespan=lifespan, 
              version="1.0",
              openapi_tags=tags_metadata)


# Mount static file handler for image files
app.mount(f"/{images_path}", StaticFiles(directory=images_path), name="images")

# Include the API key authentication as middleware
app.middleware("http")(api_key_auth)


# Add custom exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)

# Include all v1 routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return JSONResponse(content="Sliike server is running")

@app.get("/")
async def root():
    return JSONResponse(content=f"Welcome to Sliike app!")




