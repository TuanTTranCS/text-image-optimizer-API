from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(override=True)
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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



app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Initialize the database connection on startup
    app.db = get_database()
    # app.openAi_client = connect_OpenAI()

@app.on_event("shutdown")
async def shutdown_event():
    # Close the database connection on shutdown
    app.db.client.close()

    # Close OpenAI's connection on shutdown
    # app.openAi_client.close()

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
