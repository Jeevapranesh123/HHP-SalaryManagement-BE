from fastapi import HTTPException

from app.database import AsyncIOMotorClient

from app.api.utils.employees import validate_new_employee, validate_update_employee

from app.api.crud import employees as employee_crud
from app.api.controllers.salary import SalaryController

from app.schemas.request import EmployeeCreateRequest, EmployeeUpdateRequest
from app.schemas.employees import EmployeeBase

from app.schemas.salary import SalaryBase, MonthlyCompensationBase, SalaryIncentivesBase

from app.core.config import Config
from app.api.utils import *

import datetime

MONGO_DATABASE = Config.MONGO_DATABASE
LEAVE_COLLECTION = Config.LEAVE_COLLECTION


class EmployeeController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.employee_id = payload["employee_id"]
        self.employee_role = payload["primary_role"]
        self.mongo_client = mongo_client

    async def create_employee(self, employee: EmployeeCreateRequest):
        is_valid, message = await validate_new_employee(employee, self.mongo_client)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)

        emp_in_create = EmployeeBase(**employee.model_dump())

        emp = await employee_crud.create_employee(emp_in_create, self.mongo_client)

        sal_obj = SalaryController(self.payload, self.mongo_client)

        await sal_obj.create_all_salaries(emp_in_create)

        return emp

    async def get_employee(self, employee_id: str):
        if not self.employee_role in ["HR", "MD"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Forbidden")
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

        monthly_leave_days
        total_leave_days,
        total_permission_hours
        monthly_permission_hours = 0

        current_month = first_day_of_current_month()

        docs = self.mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].find(
            {
                "employee_id": employee_id,
                "status": "approved",
            }
        )

        async for i in docs:
            if i["type"] == "permission":
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
            "basic_information": {
                "employee_id": emp["employee_id"],
                "name": emp["name"],
                "email": emp["email"],
                "phone": emp["phone"],
                "department": emp["department"],
                "designation": emp["designation"],
            },
            "bank_details": emp["bank_details"],
            "address": emp["address"],
            "govt_id_proofs": emp["govt_id_proofs"],
            "basic_salary": salary_base,
            "monthly_compensation": monthly_compensation_base,
            "salary_incentives": salary_incentives_base,
            "leaves_and_permissions": {
                "total_leave_days": total_leave_days,
                "monthly_leave_days": monthly_leave_days,
                "total_permission_hours": total_permission_hours,
                "monthly_permission_hours": monthly_permission_hours,
            },
        }

        if self.employee_role == "HR" and self.employee_id == employee_id:
            pass
        elif self.employee_role == "HR":
            res["basic_salary"].pop("net_salary")
            res["basic_salary"].pop("gross_salary")
            res["monthly_compensation"].pop("other_special_allowance")
            res.pop("salary_incentives")
        # pprint.pprint(res)
        return res

    async def get_all_employees(self):
        return await employee_crud.get_all_employees(self.mongo_client)

    async def update_employee(
        self, employee_id, employee_details: EmployeeUpdateRequest
    ):
        emp_in_update = EmployeeUpdateRequest(**employee_details.model_dump())

        emp_in_update = emp_in_update.model_dump(exclude_none=True)

        emp = await employee_crud.get_employee(employee_id, self.mongo_client)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")

        is_valid, message = await validate_update_employee(
            employee_id, employee_details, self.mongo_client
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        # FIXME: Update salary if needed
        emp = await employee_crud.update_employee(
            employee_id, emp_in_update, self.mongo_client
        )

        return emp

    async def get_editable_fields(self):
        return [
            {
                "basic_information": {
                    "name": True,
                    "phone": True,
                    "department": True,
                    "designation": True,
                }
            },
            {
                "bank_details": {
                    "bank_name": True,
                    "account_number": True,
                    "ifsc_code": True,
                    "branch": True,
                    "address": True,
                }
            },
            {
                "address": {
                    "address_line_1": True,
                    "address_line_2": True,
                    "city": True,
                    "state": True,
                    "country": True,
                    "pincode": True,
                }
            },
            {
                "govt_id_proofs": {
                    "aadhar": True,
                    "pan": True,
                    "voter_id": True,
                    "driving_license": True,
                    "passport": True,
                }
            },
        ]

    async def get_create_required_fields(self):
        return [
            {"employee_id": True},
            {"name": True},
            {"email": True},
            {"phone": True},
        ]
