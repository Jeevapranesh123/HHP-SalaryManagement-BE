from app.database import AsyncIOMotorClient
from fastapi import HTTPException
from app.schemas.marketing import LocationEntry

from app.api.crud.marketing import MarketingCrud

from app.api.crud.employees import get_employee

from app.api.lib.Notification import Notification
from app.schemas.notification import (
    NotificationBase,
    SendNotification,
    NotificationMeta,
)

import datetime


class MarketingController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.mongo_client = mongo_client
        self.employee_id = payload["employee_id"]
        self.primary_role = payload["primary_role"]

    async def get_entry_meta(self):
        return {
            "data": {
                "employee_id": {
                    "type": "string",
                    "required": True,
                    "editable": False,
                },
                "type": {
                    "type": "dropdown",
                    "required": True,
                    "options": [
                        {
                            "label": "In",
                            "value": "check_in",
                        },
                        {
                            "label": "Out",
                            "value": "check_out",
                        },
                    ],
                },
                "latitude": {
                    "type": "number",
                    "required": True,
                    "editable": False,
                },
                "longitude": {
                    "type": "number",
                    "required": True,
                    "editable": False,
                },
                "date": {
                    "type": "date",
                    "required": True,
                    "editable": False,
                },
                "time": {
                    "type": "time",
                    "required": True,
                    "editable": False,
                },
                "state": {
                    "type": "string",
                    "editable": False,
                },
                "pincode": {
                    "type": "string",
                    "editable": False,
                },
                "address": {
                    "type": "textarea",
                    "required": True,
                    "editable": False,
                },
                "campaign_description": {
                    "type": "textarea",
                    "required": False,
                    "editable": True,
                },
            },
            "actions": [
                {
                    "label": "Submit",
                    "type": "button",
                    "variant": "default",
                    "action": {"url": "/marketing/entry", "method": "POST"},
                }
            ],
        }

    async def get_employees(self):
        """Get employees"""
        if not self.primary_role in ["marketing_manager", "MD"]:
            raise HTTPException(
                status_code=403,
                detail="Not Enough Permissions",
            )

        curd_obj = MarketingCrud(self.employee_id, self.mongo_client)

        if self.primary_role == "marketing_manager":
            res = await curd_obj.get_marketing_employees(self.employee_id)

        elif self.primary_role == "MD":
            res = await curd_obj.get_marketing_employees()

        return res

    async def post_entry(self, location_entry: LocationEntry):
        """Create a new location entry"""

        location_entry = location_entry.model_dump()
        print(location_entry)
        emp = await get_employee(location_entry["employee_id"], self.mongo_client)

        if not emp:
            raise HTTPException(
                status_code=404,
                detail="Employee not found",
            )

        if (
            not self.primary_role in ["MD"]
            and not self.employee_id == location_entry["employee_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="Not Enough Permissions",
            )

        if not self.primary_role in ["MD"] and not emp["is_marketing_staff"]:
            raise HTTPException(
                status_code=403,
                detail="Not Enough Permissions",
            )

        emp = await get_employee(location_entry["employee_id"], self.mongo_client)

        if not emp:
            print("emp not found")
            raise HTTPException(
                status_code=404,
                detail="Employee not found",
            )

        curd_obj = MarketingCrud(self.employee_id, self.mongo_client)

        res = await curd_obj.post_entry(location_entry)
        print(res)
        notification = Notification(
            self.employee_id, "marketing_entry", self.mongo_client
        )

        notifiers = [
            emp["employee_id"],
            emp["marketing_manager"]
            if emp["marketing_manager"]
            else "marketing_manager",
            "MD",
        ]

        entry_type = location_entry["type"].value.split("_")[1].capitalize()

        emp_notification = NotificationBase(
            title="Marketing Entry",
            description="Marketing Check {} Entry by {}".format(
                entry_type, emp["name"]
            ),
            payload={
                "url": "/marketing/{}/view?entry_id={}".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="marketing",
            source="marketing_entry",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        marketing_manager_notification = NotificationBase(
            title="Marketing Entry",
            description="Marketing Check {} Entry by {}".format(entry_type, emp["name"])
            if self.primary_role == "employee"
            else "Marketing Check {} Entry for {} by {}".format(
                entry_type, emp["name"], self.employee_id
            ),
            payload={
                "url": "/marketing/{}/view?entry_id={}".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="marketing",
            source="marketing_entry",
            target="{}".format(emp["marketing_manager"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Marketing Entry",
            description="Marketing Check {} Entry by {}".format(entry_type, emp["name"])
            if self.primary_role == "employee"
            else "Marketing Check {} Entry for {} by {}".format(
                entry_type, emp["name"], self.employee_id
            ),
            payload={
                "url": "/marketing/{}/view?entry_id={}".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="marketing",
            source="marketing_entry",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = []

        if self.primary_role == "employee":
            notifier.append(marketing_manager_notification)
            notifier.append(md_notification)

        elif self.primary_role == "marketing_manager":
            if self.employee_id == emp["employee_id"]:
                notifier.append(md_notification)
                pass
            else:
                notifier.append(emp_notification)
                notifier.append(md_notification)

        elif self.primary_role == "MD":
            if self.employee_id == emp["employee_id"]:
                pass
            else:
                notifier.append(emp_notification)
                notifier.append(marketing_manager_notification)

        send = SendNotification(notifier=notifier)

        await notification.send_notification(send)

        return res

    async def get_entries(
        self,
        employee_id: str,
        **kwargs,
    ):
        """Get all location entries"""
        date = kwargs.get("date")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        if (
            self.primary_role not in ["marketing_manager", "MD"]
            and employee_id != self.employee_id
        ):
            raise HTTPException(
                status_code=403,
                detail="Not Enough Permissions",
            )

        curd_obj = MarketingCrud(self.employee_id, self.mongo_client)

        res = await curd_obj.get_entries(
            employee_id, date=date, start_date=start_date, end_date=end_date
        )

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
                detail="Not Enough Permissions",
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

    async def get_location_entry(
        self,
        location_id: str,
    ):
        """Get all location entries"""
        curd_obj = MarketingCrud(self.employee_id, self.mongo_client)

        res = await curd_obj.get_location_entry(location_id)

        return res
