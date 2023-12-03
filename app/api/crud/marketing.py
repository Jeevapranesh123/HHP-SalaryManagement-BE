from app.core.config import Config

import datetime

from app.schemas.marketing import LocationEntry, LocationEntryInDB

MONGO_DATABASE = Config.MONGO_DATABASE
LOCATION_COLLECTION = Config.LOCATION_COLLECTION


class MarketingCrud:
    def __init__(self, caller, mongo_client):
        self.mongo_client = mongo_client
        self.employee_id = caller

    async def post_entry(self, location_entry):
        """Create a new location entry"""

        location_in_db = LocationEntryInDB(**location_entry)

        location_dict = location_in_db.model_dump()

        result = await self.mongo_client[MONGO_DATABASE][
            LOCATION_COLLECTION
        ].insert_one(location_dict)

        return True

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
