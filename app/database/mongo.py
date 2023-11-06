from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import Config


class MongoManger:
    client: AsyncIOMotorClient = None

    async def connect_to_database(self):
        logger.info("Connect to the MongoDB...")
        self.client = AsyncIOMotorClient(str(Config.MONGO_HOST))
        logger.info("Successfully connected to the MongoDB!")

    async def close_database_connection(self):
        logger.info("Close MongoDB connection...")
        self.client.close()
        logger.info("The MongoDB connection is closed!")
