from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.core.config import Config
import os

load_dotenv()

ENV = os.getenv("ENVIRONMENT")


class MongoManger:
    client: AsyncIOMotorClient = None

    def __init__(self):
        self.mongo_uri = "mongodb://{}:{}@{}:{}".format(
            Config.MONGO_USERNAME,
            Config.MONGO_PASSWORD,
            Config.MONGO_HOST,
            Config.MONGO_PORT,
        )

    async def connect_to_database(self):
        logger.info("Connect to the MongoDB...")
        if ENV == "dev":
            self.client = AsyncIOMotorClient(Config.MONGO_HOST)
        elif ENV == "prod":
            self.client = AsyncIOMotorClient(self.mongo_uri)
        else:
            raise Exception("ENV not set properly")
        logger.info("Successfully connected to the MongoDB!")

    async def close_database_connection(self):
        logger.info("Close MongoDB connection...")
        self.client.close()
        logger.info("The MongoDB connection is closed!")
