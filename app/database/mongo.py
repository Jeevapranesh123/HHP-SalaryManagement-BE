from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import Config


class MongoManger:
    client: AsyncIOMotorClient = None

    def __init__(self):
        self.mongo_uri = "mongodb://{}:{}@{}:{}".format(
            Config.MONGO_USERNAME,
            Config.MONGO_PASSWORD,
            Config.MONGO_HOST,
            Config.MONGO_PORT,
        )
        print(self.mongo_uri)

    async def connect_to_database(self):
        logger.info("Connect to the MongoDB...")
        # self.client = AsyncIOMotorClient("mongodb://root:zuvaLabs@mongodb:27017/?authMechanism=DEFAULT")
        # self.client = AsyncIOMotorClient(self.mongo_uri)
        self.client = AsyncIOMotorClient(Config.MONGO_HOST)
        logger.info("Successfully connected to the MongoDB!")

    async def close_database_connection(self):
        logger.info("Close MongoDB connection...")
        self.client.close()
        logger.info("The MongoDB connection is closed!")
