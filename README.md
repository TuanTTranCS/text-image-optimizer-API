# SLIIKE PYTHON SERVER

Sliike python apis

## Features

- AI Text generation

## Tech Stack

- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [MongoDB](https://www.mongodb.com/)
- [PyMongo](https://pymongo.readthedocs.io/en/stable/)
- [PyDantic](https://docs.pydantic.dev/latest/)

## Docs:

<!-- TODO: Add docs link -->

## Developer guide

- [Applied Coding developer guide](https://github.com/Applied-Coding/Developer-Guide/blob/main/BACKEND.md)

## Required .env file contents

```
MONGODB_URI
DB_NAME
API_KEY
OPENAI_API_KEY
OPENAI_ORGANIZATION_ID
TEXT_OPTIMIZER_PROMPT

```
### Optional variable in .env file contents (they already have default values defined in model):
```
TEXT_OPTIMIZER_MAX_INPUT_CHARACTERS
TEXT_OPTIMIZER_MAX_PROMPT_TOKEN
TEXT_OPTIMIZER_CHOICES
TEXT_OPTIMIZER_MODEL
TEXT_OPTIMIZER_TEMPERATURE
TEXT_OPTIMIZER_MAX_TOKENS
TEXT_OPTIMIZER_PROMPT
TEXT_OPTIMIZER_MAX_RETRY
```

## PIP

Ensure pip is up to date

```bash
pip install --upgrade pip
```

## Running the development server

```bash
pip install -r requirements.txt
python server.py

**For MacOS Only**
python3 server.py
```
* ***Note***: If the pip command failed to instal the tiktoken package due to missing the Rust compiler, please follow the instruction to download and install it [here](https://www.rust-lang.org/tools/install). 

Open [http://localhost:8080](http://localhost:8080) to see the server running.
The reload=True argument allows the server to restart automatically upon changes to the code.
