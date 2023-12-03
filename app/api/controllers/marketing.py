from app.database import get_mongo, AsyncIOMotorClient
from fastapi import HTTPException
from app.schemas.marketing import LocationEntry

from app.api.crud.marketing import MarketingCrud

from app.api.crud.employees import get_employee

import datetime

import pprint


class MarketingController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.mongo_client = mongo_client
        self.employee_id = payload["employee_id"]
        self.primary_role = payload["primary_role"]

    async def post_entry(self, location_entry: LocationEntry):
        """Create a new location entry"""

        location_entry = location_entry.model_dump()

        if (
            not self.primary_role in ["marketing_manager", "MD"]
            and not self.employee_id == location_entry["employee_id"]
        ):
            print("Not enough permissions")
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to perform this action",
            )

        emp = await get_employee(location_entry["employee_id"], self.mongo_client)

        if not emp:
            print("emp not found")
            raise HTTPException(
                status_code=404,
                detail="Employee not found",
            )

        if not emp["is_marketing_staff"]:
            print("not marketing staff")
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to perform this action",
            )

        curd_obj = MarketingCrud(self.employee_id, self.mongo_client)

        res = await curd_obj.post_entry(location_entry)

        return res

    async def get_entries(
        self,
        employee_id: str,
        start_date: datetime.date,
        end_date: datetime.date,
    ):
        """Get all location entries"""

        if (
            not self.primary_role in ["marketing_manager", "MD"]
            and not self.employee_id == employee_id
        ):
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to perform this action",
            )

        emp = await get_employee(employee_id, self.mongo_client)

        if not emp:
            raise HTTPException(
                status_code=404,
                detail="Employee not found",
            )

        if not emp["is_marketing_staff"]:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to perform this action",
            )

        curd_obj = MarketingCrud(self.employee_id, self.mongo_client)

        res = await curd_obj.get_entries(employee_id, start_date, end_date)

        return res

    async def get_daily_entries(
        self,
        employee_id: str,
        date: datetime.date,
    ):
        """Get all location entries"""
        if (
            employee_id
            and employee_id != self.employee_id
            and not self.primary_role in ["marketing_manager", "MD"]
        ):
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to perform this action",
            )

        if employee_id:
            emp = await get_employee(employee_id, self.mongo_client)

            if not emp:
                raise HTTPException(
                    status_code=404,
                    detail="Employee not found",
                )

        curd_obj = MarketingCrud(self.employee_id, self.mongo_client)

        res = await curd_obj.get_daily_entries(employee_id, date)

        return res
