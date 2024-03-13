# TEXT/IMAGE OPTIMIZATION REST API PYTHON SERVER

Python server to host REST API endpoints to provice text and image input optimization services with AI.

## Features

### 1. AI Text Generation/Optimization using: - OpenAI's API - Cohere's API - Anthropic's API through AWS Bedrock

* **Input validation**:

i. Text length limit (in characters)

ii. Input tokens limit (in tokens)

iii. Input words' meaninglessness: deny request if all words in the input are meaningless in English

* **Output**:

i. Configurable number of output choices count

ii. Validated output format to meet json schema

### 2. AI Image Optimization using CLAID.AI's API: Image upscaling

## Tech Stack

- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [MongoDB](https://www.mongodb.com/)
- [PyMongo](https://pymongo.readthedocs.io/en/stable/)
- [PyDantic](https://docs.pydantic.dev/latest/)
- [Amazon BedRock](https://docs.aws.amazon.com/bedrock/)

## Docs:

<!-- TODO: Add docs link -->
While the server is running, the documentation page for the API endpoint can be found at: 
- Swagger UI: [http://localhost:8080/docs](http://localhost:8080/docs)
- ReDoc UI: [http://localhost:8080/redoc](http://localhost:8080/redoc)

## Developer guide

- [Applied Coding developer guide](https://github.com/Applied-Coding/Developer-Guide/blob/main/BACKEND.md)

## Required .env file contents

```
MONGODB_URI
DB_NAME
API_KEY
OPENAI_API_KEY
OPENAI_ORGANIZATION_ID
OPENAI_TEXT_GEN_PROMPT

COHERE_API_KEY
COHERE_TEXT_GEN_PROMPT
COHERE_CLIENT_NAME

AWS_DEFAULT_REGION
AWS_PROFILE
ANTHROPIC_TEXT_GEN_PROMPT

CLAID_API_KEY
```
### Optional variable in .env file contents (they already have default values defined in model):
```
TEXT_OPTIMIZER_MAX_INPUT_CHARACTERS
TEXT_OPTIMIZER_MAX_PROMPT_TOKEN
TEXT_OPTIMIZER_CHOICES
OPENAI_TEXT_GEN_MODEL
COHERE_TEXT_GEN_MODEL
ANTHROPIC_TEXT_GEN_MODEL
TEXT_OPTIMIZER_TEMPERATURE
ANTHROPIC_TEXT_GEN_TEMPERATURE
TEXT_OPTIMIZER_MAX_TOKENS
TEXT_OPTIMIZER_MAX_RETRY
CLAID_API_HOST
IMAGES_PATH
```

## PIP

Ensure pip is up to date

```bash
pip install --upgrade pip
```

## Setup Anthropic Bedrock access from local PC

In order to run the Anthropic model(s) on AWS Bedrock, need to perform the follow steps:

1. Use AWS root account to create a new IAM user
2. Add the policy to access bedrock to the user in IAM
3. Enable console access for the IAM user (i.e: *bedrock_admin*)
4. Login with the IAM user account, go to Bedrock and ask for permission of Claude models (use case need to be provided)
5. Create a CLI access key and export into csv file
6. Add *'User Name'* column header and value into before the first column in the csv file, save as UTF-8 format
7. Import the csv file into AWS CLI ([reference](https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html))
8. Add the created profile name (same as user name, *bedrock_admin* from step 3) into the AWS_PROFILE variable in the .env file



## Running the development server

**_Notes_:** The environment was tested using Python 3.11.8. Using a higher Python version might cause error during installing some packages.

```bash
pip install -r requirements.txt
python server.py
```

**For MacOS Only**
```bash
python3 server.py
```
* ***Note***: If the pip command failed to instal the tiktoken package due to missing the Rust compiler, please follow the instruction to download and install it [here](https://www.rust-lang.org/tools/install). 

Open [http://localhost:8080](http://localhost:8080) to see the server running.
The reload=True argument allows the server to restart automatically upon changes to the code.

