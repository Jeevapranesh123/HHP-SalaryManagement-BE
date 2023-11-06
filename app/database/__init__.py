from motor.motor_asyncio import AsyncIOMotorClient
from app.database.mongo import MongoManger


mongo = MongoManger()


async def get_mongo() -> AsyncIOMotorClient:
    return mongo.client
