from pymongo import MongoClient
from os import getenv

DATABASE_CLIENT = None

def get_database():
    global DATABASE_CLIENT
    if DATABASE_CLIENT is None:
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        MONGODB_URI = getenv("MONGODB_URI")
        DB_NAME = getenv("DB_NAME")

        # Create a connection using MongoClient.
        DATABASE_CLIENT = MongoClient(MONGODB_URI)

    # Create the database for our example (we will use the same database throughout the tutorial)
    return DATABASE_CLIENT[DB_NAME]

