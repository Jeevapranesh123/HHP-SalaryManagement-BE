from app.database import AsyncIOMotorClient
from fastapi import HTTPException
from functools import wraps

import datetime

from app.schemas.request import (
    PostSalaryRequest,
    PostMonthlyCompensationRequest,
    PostSalaryIncentivesRequest,
    SalaryAdvanceRequest,
    SalaryAdvanceRespondRequest,
)
from app.schemas.salary import (
    SalaryBase,
    MonthlyCompensationBase,
    SalaryIncentivesBase,
    SalaryAdvanceBase,
)

from app.api.crud import salary as salary_crud
from app.api.crud import employees as employee_crud
from app.api.crud import auth as auth_crud

from app.api.lib.Notification import Notification
from app.schemas.notification import (
    NotificationBase,
    SendNotification,
    NotificationMeta,
)

from app.api.utils import *


from app.core.config import Config

MONGO_DATABASE = Config.MONGO_DATABASE
LEAVE_COLLECTION = Config.LEAVE_COLLECTION


def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # args[0] is the 'self' parameter for class methods
            if args[0].employee_role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Not enough permissions")
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class SalaryController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.employee_id = payload["employee_id"]
        self.employee_role = payload["primary_role"]
        self.employee_name = payload["employee_name"]
        self.mongo_client = mongo_client

    async def get_all_salaries(self):
        return await salary_crud.get_all_salaries(self.mongo_client)

    async def get_salary_meta(self):
        salary_base = SalaryBase(employee_id=self.employee_id).model_dump(
            exclude={"employee_id"}
        )

        salary_base["net_salary"] = None

        monthly_compensation_base = MonthlyCompensationBase(
            employee_id=self.employee_id
        ).model_dump(exclude={"employee_id"})

        salary_incentives_base = SalaryIncentivesBase(
            employee_id=self.employee_id
        ).model_dump(exclude={"employee_id"})

        res = {
            "basic_salary": {
                "data": {
                    k: {
                        "type": "number",
                        "editable": True if k != "net_salary" else False,
                    }
                    for k, v in salary_base.items()
                },
                "actions": [
                    {
                        "label": "Submit",
                        "type": "button",
                        "variant": "default",
                        "action": {"url": "/salary/post_salary", "method": "PUT"},
                    }
                ],
            },
            "monthly_compensation": {
                "data": {
                    k: {
                        "type": "number",
                        "editable": True,
                    }
                    for k, v in monthly_compensation_base.items()
                },
                "actions": [
                    {
                        "label": "Submit",
                        "type": "button",
                        "variant": "default",
                        "action": {
                            "url": "/salary/post_monthly_compensation",
                            "method": "PUT",
                        },
                    }
                ],
            },
            "salary_incentives": {
                "data": {
                    k: {
                        "type": "number",
                        "editable": True,
                    }
                    for k, v in salary_incentives_base.items()
                },
                "actions": [
                    {
                        "label": "Submit",
                        "type": "button",
                        "variant": "default",
                        "action": {
                            "url": "/salary/post_salary_incentives",
                            "method": "PUT",
                        },
                    }
                ],
            },
            "leaves_and_permissions": {
                "data": {
                    "total_leave_days": {
                        "type": "string",
                        "editable": False,
                    },
                    "monthly_leave_days": {
                        "type": "string",
                        "editable": False,
                    },
                    "total_permission_hours": {
                        "type": "string",
                        "editable": False,
                    },
                    "monthly_permission_hours": {
                        "type": "string",
                        "editable": False,
                    },
                },
                "actions": [],
            },
        }

        if self.employee_role == "HR":
            res["basic_salary"]["data"].pop("net_salary")
            res["basic_salary"]["data"].pop("gross_salary")
            res["monthly_compensation"]["data"].pop("other_special_allowance")
            res.pop("salary_incentives")

        return res

    async def get_salary(self, employee_id: str):
        if not self.employee_role in ["HR", "MD"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        emp = await employee_crud.get_employee_with_salary(
            employee_id, self.mongo_client
        )

        salary_base = SalaryBase(**emp)
        salary_base = salary_base.model_dump(exclude={"employee_id"})
        salary_base["net_salary"] = emp["net_salary"]

        monthly_compensation_base = MonthlyCompensationBase(**emp)
        monthly_compensation_base = monthly_compensation_base.model_dump(
            exclude={"employee_id"}
        )

        salary_incentives_base = SalaryIncentivesBase(**emp)
        salary_incentives_base = salary_incentives_base.model_dump(
            exclude={"employee_id"}
        )

        monthly_leave_days = (
            total_leave_days
        ) = total_permission_hours = monthly_permission_hours = 0

        current_month = first_day_of_current_month()

        docs = self.mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].find(
            {
                "employee_id": employee_id,
                "status": "approved",
            }
        )

        async for i in docs:
            if i["leave_type"] == "permission":
                if i["month"] == current_month:
                    monthly_permission_hours += i["no_of_hours"]
                total_permission_hours += i["no_of_hours"]
            else:
                if i["month"] == current_month:
                    monthly_leave_days += i["no_of_days"]
                total_leave_days += i["no_of_days"]

        monthly_permission_hours = "{} Hours {} Minutes".format(
            str(datetime.timedelta(hours=monthly_permission_hours)).split(":")[0],
            str(datetime.timedelta(hours=monthly_permission_hours)).split(":")[1],
        )
        total_permission_hours = "{} Hours {} Minutes".format(
            str(datetime.timedelta(hours=total_permission_hours)).split(":")[0],
            str(datetime.timedelta(hours=total_permission_hours)).split(":")[1],
        )

        res = {
            "basic_salary": {k: v for k, v in salary_base.items()},
            "monthly_compensation": {
                k: v for k, v in monthly_compensation_base.items()
            },
            "salary_incentives": {k: v for k, v in salary_incentives_base.items()},
            "leaves_and_permissions": {
                "total_leave_days": total_leave_days,
                "monthly_leave_days": monthly_leave_days,
                "total_permission_hours": total_permission_hours,
                "monthly_permission_hours": monthly_permission_hours,
            },
        }

        if self.employee_role == "employee" and self.employee_id != employee_id:
            return HTTPException(status_code=403, detail="Not enough permissions")

        elif self.employee_role == "HR":
            res["basic_salary"].pop("net_salary")
            res["basic_salary"].pop("gross_salary")
            res["monthly_compensation"].pop("other_special_allowance")
            res.pop("salary_incentives")

        return res

    async def get_salary_advance_history(self, employee_id: str, status):
        if not self.employee_role in ["MD"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        res = await salary_crud.get_salary_advance_history(
            employee_id, status, self.mongo_client
        )
        for i in res:
            i["requested_date"] = datetime.datetime.strftime(
                i["requested_at"], "%d-%m-%Y"
            )

        return res

    async def get_salary_history(self, employee_id: str):
        if not self.employee_role in ["MD", "HR"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        res = await salary_crud.get_salary_history(employee_id, self.mongo_client)

        if self.employee_role == "HR" and self.employee_id == employee_id:
            pass

        elif self.employee_role == "HR":
            for i in res:
                i.pop("gross_salary")

        return res

    async def get_monthly_compensation_history(self, employee_id: str):
        if not self.employee_role in ["MD", "HR"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        res = await salary_crud.get_monthly_compensation_history(
            employee_id, self.mongo_client
        )

        if self.employee_role == "HR" and self.employee_id == employee_id:
            pass

        elif self.employee_role == "HR":
            for i in res:
                i.pop("other_special_allowance")

        return res

    async def get_salary_incentives_history(self, employee_id: str):
        if not self.employee_role in ["MD"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return await salary_crud.get_salary_incentives_history(
            employee_id, self.mongo_client
        )

    async def get_salary_advance(self, salary_advance_id: str):
        salary_advance = await salary_crud.get_salary_advance(
            salary_advance_id, self.mongo_client
        )
        if not salary_advance:
            raise HTTPException(
                status_code=404, detail="Salary Advance Record not found"
            )
        if (
            not self.employee_role in ["MD"]
            and salary_advance["employee_id"] != self.employee_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return salary_advance

    async def create_all_salaries(self, emp_in_create):
        emp_in_create = emp_in_create.model_dump()
        salary_base = SalaryBase(
            employee_id=emp_in_create["employee_id"],
        )

        await self.create_salary(salary_base)

        monthly_variable_compensation_base = MonthlyCompensationBase(
            employee_id=emp_in_create["employee_id"],
        )

        await self.create_monthly_compensation(monthly_variable_compensation_base)

        salary_extras_base = SalaryIncentivesBase(
            employee_id=emp_in_create["employee_id"],
        )

        await self.create_salary_incentives(salary_extras_base)

    async def create_salary(self, SalaryBase: SalaryBase):
        return await salary_crud.create_salary(SalaryBase, self.mongo_client)

    async def create_monthly_compensation(
        self, MonthlyCompensationBase: MonthlyCompensationBase
    ):
        return await salary_crud.create_monthly_compensation(
            MonthlyCompensationBase, self.mongo_client
        )

    async def create_salary_incentives(
        self, SalaryIncentivesBase: SalaryIncentivesBase
    ):
        return await salary_crud.create_salary_incentives(
            SalaryIncentivesBase, self.mongo_client
        )

    @role_required(["HR", "MD"])
    async def post_salary(self, PostSalaryRequest: PostSalaryRequest):
        if self.employee_role == "HR":
            PostSalaryRequest.gross_salary = None
        salary_in_create = SalaryBase(**PostSalaryRequest.model_dump())
        emp = await employee_crud.get_employee(
            salary_in_create.employee_id, self.mongo_client
        )
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        res = await salary_crud.update_salary(
            salary_in_create, self.mongo_client, self.payload["employee_id"]
        )

        user = await auth_crud.get_user_with_employee_id(
            salary_in_create.employee_id, self.mongo_client
        )

        branch = emp["branch"]

        notification = Notification(self.employee_id, "post_salary", self.mongo_client)
        notifiers = [salary_in_create.employee_id, "HR", "MD"]
        employee_notification = NotificationBase(
            title="Salary Updated",
            description="Your salary has been updated by {}".format(self.employee_name),
            payload={
                "url": "/salary/basic",
            },
            ui_action="action",
            type="salary",
            source="post_salary",
            target=salary_in_create.employee_id,
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        hr_notification = NotificationBase(
            title="Salary Updated",
            description="Salary has been updated for {} by {}".format(
                user["info"]["name"], self.employee_name
            ),
            payload={
                "url": "/employees/{}".format(salary_in_create.employee_id),
            },
            ui_action="action",
            type="salary",
            source="post_salary",
            target="HR_{}".format(branch.replace(" ", "_")),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Salary Updated",
            description="Salary has been updated for {} by {}".format(
                user["info"]["name"], self.employee_name
            ),
            payload={
                "url": "/employees/{}".format(salary_in_create.employee_id),
            },
            ui_action="action",
            type="salary",
            source="post_salary",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = [employee_notification]

        user_role = user["primary_role"]["role"]

        if self.employee_role == "MD":
            if user_role == "HR":
                pass
            else:
                if salary_in_create.pf != 0 or salary_in_create.esi != 0:
                    notifier.append(hr_notification)

        elif self.employee_role == "HR":
            if user_role == "MD":
                pass

            else:
                notifier.append(md_notification)

        send = SendNotification(
            notifier=notifier,
        )

        await notification.send_notification(send)

        return res

    @role_required(["HR", "MD"])
    async def post_monthly_compensation(
        self, PostMonthlyCompensationRequest: PostMonthlyCompensationRequest
    ):
        if self.employee_role == "HR":
            PostMonthlyCompensationRequest.other_special_allowance = None
        monthly_compensation_in_create = MonthlyCompensationBase(
            **PostMonthlyCompensationRequest.model_dump()
        )
        emp = await employee_crud.get_employee(
            PostMonthlyCompensationRequest.employee_id, self.mongo_client
        )
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        res = await salary_crud.update_monthly_compensation(
            monthly_compensation_in_create,
            self.mongo_client,
            self.payload["employee_id"],
        )

        user = await auth_crud.get_user_with_employee_id(
            monthly_compensation_in_create.employee_id, self.mongo_client
        )

        branch = emp["branch"]

        notification = Notification(
            self.employee_id, "post_monthly_compensation", self.mongo_client
        )

        notifiers = [monthly_compensation_in_create.employee_id, "HR", "MD"]

        employee_notification = NotificationBase(
            title="Monthly Compensation Updated",
            description="Your monthly compensation has been updated by {}".format(
                self.employee_name
            ),
            payload={
                "url": "/salary/monthly-compensation",
            },
            ui_action="action",
            type="salary",
            source="post_monthly_compensation",
            target=monthly_compensation_in_create.employee_id,
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        hr_notification = NotificationBase(
            title="Monthly Compensation Updated",
            description="Monthly Compensation has been updated for {} by {}".format(
                user["info"]["name"], self.employee_name
            ),
            payload={
                "url": "/employees/{}".format(
                    monthly_compensation_in_create.employee_id
                ),
            },
            ui_action="action",
            type="salary",
            source="post_monthly_compensation",
            target="HR_{}".format(branch.replace(" ", "_")),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Monthly Compensation Updated",
            description="Monthly Compensation has been updated for {} by {}".format(
                user["info"]["name"], self.employee_name
            ),
            payload={
                "url": "/employees/{}".format(
                    monthly_compensation_in_create.employee_id
                ),
            },
            ui_action="action",
            type="salary",
            source="post_monthly_compensation",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = [employee_notification]

        user_role = user["primary_role"]["role"]

        if self.employee_role == "MD":
            if user_role == "HR":
                pass
            else:
                notifier.append(hr_notification)

        elif self.employee_role == "HR":
            if user_role == "MD":
                pass
            else:
                notifier.append(md_notification)

        send = SendNotification(
            notifier=notifier,
        )

        await notification.send_notification(send)

        return res

    @role_required(["MD"])
    async def post_salary_incentives(
        self, PostSalaryIncentivesRequest: PostSalaryIncentivesRequest
    ):
        salary_incentives_in_create = SalaryIncentivesBase(
            **PostSalaryIncentivesRequest.model_dump()
        )
        emp = await employee_crud.get_employee(
            PostSalaryIncentivesRequest.employee_id, self.mongo_client
        )

        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        res = await salary_crud.update_salary_incentives(
            salary_incentives_in_create,
            self.mongo_client,
            self.payload["employee_id"],
        )

        notification = Notification(
            self.employee_id, "post_salary_incentives", self.mongo_client
        )

        notifiers = [salary_incentives_in_create.employee_id]

        employee_notification = NotificationBase(
            title="Salary Incentives Updated",
            description="Your salary incentives have been updated by {}".format(
                self.employee_name
            ),
            payload={
                "url": "/salary/incentives",
            },
            ui_action="action",
            type="salary",
            source="post_salary_incentives",
            target=salary_incentives_in_create.employee_id,
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        send = SendNotification(
            notifier=[employee_notification],
        )

        await notification.send_notification(send)

        return res

    @role_required(["MD"])
    async def post_advance(self, SalaryAdvanceRequest: SalaryAdvanceRequest):
        salary_advance_in_create = SalaryAdvanceRequest.model_dump(exclude_none=True)
        emp = await employee_crud.get_employee(
            salary_advance_in_create["employee_id"], self.mongo_client
        )
        if not emp:
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(
                    salary_advance_in_create["employee_id"]
                ),
            )

        res = await salary_crud.request_advance(
            salary_advance_in_create, self.mongo_client, "post", self.employee_id
        )
        res["salary_advance_id"] = res["id"]

        notification = Notification(self.employee_id, "post_advance", self.mongo_client)

        notifiers = [salary_advance_in_create["employee_id"]]

        employee_notification = NotificationBase(
            title="Salary Advance Posted",
            description="Your salary advance has been posted by {}".format(
                self.employee_name
            ),
            payload={
                "url": "/salary-advance/history",
            },
            ui_action="action",
            type="salary",
            source="post_advance",
            target=salary_advance_in_create["employee_id"],
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        send = SendNotification(
            notifier=[employee_notification],
        )

        await notification.send_notification(send)

        return res

    async def request_advance(self, SalaryAdvanceRequest: SalaryAdvanceRequest):
        salary_advance_in_create = SalaryAdvanceRequest.model_dump(exclude_none=True)

        if (
            not self.employee_role in ["HR", "MD"]
            and salary_advance_in_create["employee_id"] != self.employee_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        emp = await employee_crud.get_employee(
            salary_advance_in_create["employee_id"], self.mongo_client
        )
        if not emp:
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(
                    salary_advance_in_create["employee_id"]
                ),
            )

        res = await salary_crud.request_advance(
            salary_advance_in_create, self.mongo_client, "request", self.employee_id
        )
        res["salary_advance_id"] = res["id"]

        user = await auth_crud.get_user_with_employee_id(
            salary_advance_in_create["employee_id"], self.mongo_client
        )

        notification = Notification(
            self.employee_id, "request_advance", self.mongo_client
        )

        notifiers = [salary_advance_in_create["employee_id"], "MD"]

        employee_notification = NotificationBase(
            title="Salary Advance Requested",
            description="Your salary advance has been requested by {}".format(
                self.employee_name
            ),
            payload={
                "url": "/profile",
            },
            ui_action="action",
            type="salary",
            source="request_advance",
            target=salary_advance_in_create["employee_id"],
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Salary Advance Requested",
            description="Salary Advance has been requested for {} by {}".format(
                user["info"]["name"], self.employee_name
            )
            if self.employee_role == "HR"
            else "Salary Advance has been requested by {}".format(self.employee_name),
            payload={
                "url": "/employees/{}/advance-salary/respond?id={}".format(
                    salary_advance_in_create["employee_id"], res["id"]
                ),
            },
            ui_action="action",
            type="salary",
            source="request_advance",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = []

        if self.employee_role == "MD":
            notifier.append(employee_notification)

        elif self.employee_role == "HR":
            notifier.append(md_notification)
            notifier.append(employee_notification)

        elif self.employee_role == "employee":
            notifier.append(md_notification)

        send = SendNotification(
            notifier=notifier,
        )

        await notification.send_notification(send)

        return res

    @role_required(["MD"])
    async def respond_salary_advance(
        self,
        SalaryAdvanceRespondRequest: SalaryAdvanceRespondRequest,
    ):
        salary_advance_in_create = SalaryAdvanceRespondRequest.model_dump()

        if not await salary_crud.get_salary_advance(
            salary_advance_in_create["id"], self.mongo_client
        ):
            raise HTTPException(
                status_code=404, detail="Salary Advance Record not found"
            )
        res = await salary_crud.respond_salary_advance(
            salary_advance_in_create, self.employee_id, self.mongo_client
        )

        notification = Notification(
            self.employee_id, "respond_salary_advance", self.mongo_client
        )

        notifiers = [res["employee_id"]]

        employee_notification = NotificationBase(
            title="Salary Advance {}".format(res["status"].capitalize()),
            description="Your salary advance request has been {} by {}".format(
                res["status"].lower(), self.employee_name
            ),
            payload={
                "url": "/salary-advance/history",
            },
            ui_action="action",
            type="salary",
            source="respond_salary_advance",
            target=res["employee_id"],
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        send = SendNotification(
            notifier=[employee_notification],
        )

        await notification.send_notification(send)

        return res
