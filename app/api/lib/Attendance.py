from app.core.config import Config
import datetime

from app.schemas.attendance import AttendanceBase, AttendanceInDB

MONGO_DATABASE = Config.MONGO_DATABASE
ATTENDANCE_COLLECTION = Config.ATTENDANCE_COLLECTION
LEAVE_COLLECTION = Config.LEAVE_COLLECTION
EMPLOYEE_COLLECTION = Config.EMPLOYEE_COLLECTION


class Attendance:
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client

    async def get_attendance(self, employee_id):
        return await self.mongo_client[MONGO_DATABASE][ATTENDANCE_COLLECTION].find_one(
            {"employee_id": employee_id}
        )

    async def update_attendance(self, employee_id, attendance):
        pass

    async def post_attendance(self):
        x = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(1, 32):
            today = x + datetime.timedelta(days=i)
            if today.isoweekday() in [6, 7]:
                continue
            current_month = today.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            leave_record = (
                await self.mongo_client[MONGO_DATABASE][LEAVE_COLLECTION]
                .find({"month": current_month, "status": "approved"})
                .to_list(1000)
            )

            absent_list = []

            if leave_record:
                for record in leave_record:
                    end_date = record.get("end_date")
                    start_date = record.get("start_date")

                    if not end_date:
                        end_date = start_date

                    if start_date <= today <= end_date:
                        absent_list.append(record.get("employee_id"))

            employee_list = await self.mongo_client[MONGO_DATABASE][
                EMPLOYEE_COLLECTION
            ].distinct("employee_id")

            present_list = list(set(employee_list) - set(absent_list))

            attendance_list = []

            for employee_id in present_list:
                attendance_list.append(
                    AttendanceInDB(
                        employee_id=employee_id, date=today, status="present"
                    ).model_dump()
                )

            for employee_id in absent_list:
                attendance_list.append(
                    AttendanceInDB(
                        employee_id=employee_id, date=today, status="absent"
                    ).model_dump()
                )

            await self.mongo_client[MONGO_DATABASE][ATTENDANCE_COLLECTION].insert_many(
                attendance_list
            )

    async def delete_attendance(self, employee_id):
        pass

    async def get_attendance_by_date(self, employee_id, date):
        pass

    async def get_attendance_by_month(self, employee_id, month):
        pass

    async def get_attendance_by_year(self, employee_id, year):
        pass

    async def get_attendance_by_date_range(self, employee_id, start_date, end_date):
        pass

    async def get_attendance_by_month_range(self, employee_id, start_month, end_month):
        pass

    async def get_attendance_by_year_range(self, employee_id, start_year, end_year):
        pass
