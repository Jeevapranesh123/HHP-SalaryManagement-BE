from app.core.config import Config

import datetime

from app.schemas.marketing import LocationEntry, LocationEntryInDB

MONGO_DATABASE = Config.MONGO_DATABASE
LOCATION_COLLECTION = Config.LOCATION_COLLECTION
EMPLOYEE_COLLECTION = Config.EMPLOYEE_COLLECTION


class MarketingCrud:
    def __init__(self, caller, mongo_client):
        self.mongo_client = mongo_client
        self.employee_id = caller

    async def get_marketing_employees(self, manager_id=None):
        """Get employees"""

        query = {
            "is_marketing_staff": True,
        }

        if manager_id:
            query["marketing_manager"] = manager_id

        employees = (
            await self.mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION]
            .find(
                query,
                {
                    "_id": 0,
                    "employee_id": 1,
                    "name": 1,
                    "email": 1,
                    "phone": 1,
                    "branch": 1,
                },
            )
            .to_list(length=1000)
        )

        return employees

    async def get_entries(self, employee_id, **kwargs):
        date = kwargs.get("date")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        query = {}

        if date:
            date = datetime.datetime.combine(date, datetime.time.min)
            query["date"] = date

        if start_date and end_date:
            if query.get("date"):
                query.pop("date")
            start_date = datetime.datetime.combine(start_date, datetime.time.min)
            end_date = datetime.datetime.combine(end_date, datetime.time.max)
            query["date"] = {"$gte": start_date, "$lte": end_date}

        if employee_id:
            query["employee_id"] = employee_id

        entries = (
            await self.mongo_client[MONGO_DATABASE][LOCATION_COLLECTION]
            .find(query, {"_id": 0})
            .to_list(length=1000)
        )

        return entries

    async def post_entry(self, location_entry):
        """Create a new location entry"""

        location_in_db = LocationEntryInDB(**location_entry)

        location_dict = location_in_db.model_dump()

        result = await self.mongo_client[MONGO_DATABASE][
            LOCATION_COLLECTION
        ].insert_one(location_dict)

        return location_dict

    async def get_daily_entries(self, employee_id, date):
        """Get daily entries"""

        start_date = datetime.datetime.combine(date, datetime.time.min)
        end_date = datetime.datetime.combine(date, datetime.time.max)

        query = {
            "date": {"$gte": start_date, "$lte": end_date},
        }
        if employee_id:
            query["employee_id"] = employee_id

        entries = (
            await self.mongo_client[MONGO_DATABASE][LOCATION_COLLECTION]
            .find(query, {"_id": 0})
            .to_list(length=1000)
        )

        return entries

    async def get_location_entry(self, entry_id):
        """Get location entry"""

        query = {
            "id": entry_id,
        }

        entry = await self.mongo_client[MONGO_DATABASE][LOCATION_COLLECTION].find_one(
            query, {"_id": 0}
        )

        return entry
