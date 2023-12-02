from app.database import AsyncIOMotorClient


class AttendanceController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.mongo_client = mongo_client
        self.payload = payload
        self.employee_id = payload["employee_id"]
        self.primary_role = payload["primary_role"]
        self.branch = payload["branch"]

    async def get_attendance(self, employee_id, **kwargs):
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        month = kwargs.get("month")
