from app.database import AsyncIOMotorClient


class AttendanceController:
    def __init__(self, employee_id, mongo_client: AsyncIOMotorClient):
        self.mongo_client = mongo_client
        self.employee_id = employee_id
