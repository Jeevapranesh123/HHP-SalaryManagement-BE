from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.core.config import Config
import os
import json
from pymongo import IndexModel, ASCENDING, DESCENDING

load_dotenv()

ENV = os.getenv("ENVIRONMENT")


class MongoManger:
    client: AsyncIOMotorClient = None

    def __init__(self):
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
        await self.create_indexes()
        logger.info("Successfully connected to the MongoDB!")

    async def close_database_connection(self):
        logger.info("Close MongoDB connection...")
        await self.drop_indexes()
        self.client.close()
        logger.info("The MongoDB connection is closed!")

    async def create_roles(self):
        # Read JSON file

        with open("roles.json") as f:
            data = json.load(f)

        logger.info("Creating Roles")
        # Insert data into collection
        for i in data["roles"]:
            self.client[Config.MONGO_DATABASE]["roles"].update_one(
                {"role": i["role"]}, {"$set": i}, upsert=True
            )

    async def create_indexes(self):
        with open(Config.INDEX_CONFIG_FILE_LOCATION) as f:
            data = json.load(f)

        logger.info("Creating Indexes")
        for i in data["indexes"]:
            if i["fields"] == []:
                continue
            index = IndexModel(i["fields"], unique=i.get("unique", False))
            self.client[Config.MONGO_DATABASE][i["collection"]].create_indexes([index])

    async def drop_indexes(self):
        collections = await self.client[Config.MONGO_DATABASE].list_collection_names()
        logger.info("Dropping Indexes")
        for collection in collections:
            print(collection)
            if collection == "Get Profile":
                continue
            await self.client[Config.MONGO_DATABASE][collection].drop_indexes()
