from os import getenv

from app.utils import bedrock, print_ww

BEDROCK_CLIENT = None

def connect_Bedrock():
    global BEDROCK_CLIENT
    if BEDROCK_CLIENT is None:
        pass
        BEDROCK_ASSUME_ROLE = getenv("BEDROCK_ASSUME_ROLE", None)
        AWS_DEFAULT_REGION = getenv("AWS_DEFAULT_REGION", None)
        BEDROCK_CLIENT = bedrock.get_bedrock_client(
        assumed_role=BEDROCK_ASSUME_ROLE,
        region=AWS_DEFAULT_REGION
        # runtime=False
        )

    return BEDROCK_CLIENT