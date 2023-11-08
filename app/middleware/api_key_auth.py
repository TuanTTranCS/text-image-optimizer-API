from fastapi import Request
from fastapi.responses import JSONResponse
from os import getenv

API_KEY = getenv("API_KEY")


async def api_key_auth(request: Request, call_next):
    # List of endpoints to exclude from API key requirement
    excluded_paths = ["/health", "/", "/docs", "/openapi.json", "/redoc"]

    if request.url.path not in excluded_paths:
        api_key = request.headers.get("X-API-KEY")
        expected_api_key = API_KEY

        if api_key != expected_api_key:
            return JSONResponse(status_code=403, content={"detail": "Invalid API Key"})

    response = await call_next(request)
    return response
