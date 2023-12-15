from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.core.config import Config
import os
import json

load_dotenv()

ENV = os.getenv("ENVIRONMENT")


class MongoManger:
    client: AsyncIOMotorClient = None

    def __init__(self):
        print(
            Config.MONGO_HOST,
            Config.MONGO_PORT,
            Config.MONGO_USERNAME,
            Config.MONGO_PASSWORD,
        )
        self.mongo_uri = None

        if ENV == "dev":
            self.mongo_uri = "mongodb://{}:{}/".format(
                Config.MONGO_HOST, Config.MONGO_PORT
            )

        elif ENV == "prod" or ENV == "staging":
            self.mongo_uri = "mongodb://{}:{}@{}:{}".format(
                Config.MONGO_USERNAME,
                Config.MONGO_PASSWORD,
                Config.MONGO_HOST,
                Config.MONGO_PORT,
            )

        else:
            self.mongo_uri = "mongodb://{}:{}/".format(
                Config.MONGO_HOST, Config.MONGO_PORT
            )

    async def connect_to_database(self):
        logger.info("Connect to the MongoDB...")
        self.client = AsyncIOMotorClient(self.mongo_uri)
        await self.create_roles()
        logger.info("Successfully connected to the MongoDB!")

    async def close_database_connection(self):
        logger.info("Close MongoDB connection...")
        self.client.close()
        logger.info("The MongoDB connection is closed!")

    async def create_roles(self):
        # Read JSON file
        import os 
        print(os.getcwd())
        print(os.listdir())
        with open("roles.json") as f:
            data = json.load(f)

        # Insert data into collection
        for i in data["roles"]:
            print(i)
            self.client[Config.MONGO_DATABASE]["roles"].update_one({"role": i["role"]}, {"$set": i}, upsert=True)