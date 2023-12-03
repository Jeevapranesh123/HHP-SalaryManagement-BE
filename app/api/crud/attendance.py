from app.database import AsyncIOMotorClient

from app.core.config import Config

MONGO_DATABASE = Config.MONGO_DATABASE
ATTENDANCE_COLLECTION = Config.ATTENDANCE_COLLECTION


async def get_attendance(employee_id, month, mongo_client: AsyncIOMotorClient):
    pass
