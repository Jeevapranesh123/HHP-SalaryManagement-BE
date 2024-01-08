from app.schemas.employees import EmployeeBase
from app.schemas.db import EmployeeInDB
from app.schemas.request import EmployeeUpdateRequest
from app.database import AsyncIOMotorClient
from app.core.config import Config
from app.api.utils.employees import generate_random_password, hash_password
from app.schemas.salary import SalaryBase, MonthlyCompensationBase, SalaryIncentivesBase
from app.schemas.auth import UserBase
import uuid
from fastapi import HTTPException
from app.api.utils import *
from datetime import datetime, timezone, timedelta
from app.core import pipelines


MONGO_DATABASE = Config.MONGO_DATABASE
EMPLOYEE_COLLECTION = Config.EMPLOYEE_COLLECTION
USERS_COLLECTION = Config.USERS_COLLECTION
ROLES_COLLECTION = Config.ROLES_COLLECTION
LEAVE_COLLECTION = Config.LEAVE_COLLECTION
ATTENDANCE_COLLECTION = Config.ATTENDANCE_COLLECTION


async def get_employee_with_computed_fields(employee_id, mongo_client, month=None):
    emp = await get_employee_with_salary(employee_id, mongo_client, month)

    salary_base = SalaryBase(**emp)
    salary_base = salary_base.model_dump(exclude={"employee_id"})
    salary_base["net_salary"] = emp["net_salary"]

    monthly_compensation_base = MonthlyCompensationBase(**emp)
    monthly_compensation_base = monthly_compensation_base.model_dump(
        exclude={"employee_id"}
    )

    salary_incentives_base = SalaryIncentivesBase(**emp)
    salary_incentives_base = salary_incentives_base.model_dump(exclude={"employee_id"})

    monthly_leave_days = (
        total_leave_days
    ) = total_permission_hours = monthly_permission_hours = 0

    # current_month = first_day_of_current_month()
    current_month = first_day_of_last_month()

    docs = mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].find(
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
        str(timedelta(hours=monthly_permission_hours)).split(":")[0],
        str(timedelta(hours=monthly_permission_hours)).split(":")[1],
    )
    total_permission_hours = "{} Hours {} Minutes".format(
        str(timedelta(hours=total_permission_hours)).split(":")[0],
        str(timedelta(hours=total_permission_hours)).split(":")[1],
    )

    last_day = last_day_of_last_month()
    current_month = first_day_of_last_month()
    print(current_month, last_day)
    attendance = mongo_client[MONGO_DATABASE][ATTENDANCE_COLLECTION].find(
        {"employee_id": employee_id, "date": {"$gte": current_month, "$lte": last_day}}
    )
    present = 0
    absent = 0
    async for i in attendance:
        if i["status"] == "present":
            present += 1
        elif i["status"] == "absent":
            absent += 1

    total_working_days = present + absent
    total_present_days = present
    total_absent_days = absent
    present_percentage = (
        (present / total_working_days) * 100
        if total_working_days != 0 and present != 0
        else 0
    )
    res = {
        "basic_information": {
            "employee_id": emp["employee_id"],
            "name": emp["name"],
            "email": emp["email"],
            "phone": emp["phone"],
            "department": emp["department"],
            "designation": emp["designation"],
            "branch": emp["branch"],
            "profile_image": emp["profile_image"],
        },
        "bank_details": emp["bank_details"],
        "address": emp["address"],
        "govt_id_proofs": emp["govt_id_proofs"],
        "basic_salary": salary_base,
        "monthly_compensation": monthly_compensation_base,
        "salary_incentives": salary_incentives_base,
        "loan_and_advance": {
            "loan": emp["loan"],
            "salary_advance": emp["salary_advance"],
        },
        "late_entry": {
            "late_hours_loss_of_pay": emp["late_entry"],
        },
        "leaves_and_permissions": {
            "total_leave_days": total_leave_days,
            "monthly_leave_days": monthly_leave_days,
            "total_permission_hours": total_permission_hours,
            "monthly_permission_hours": monthly_permission_hours,
        },
        "attendance": {
            "total_working_days": total_working_days,
            "total_present_days": total_present_days,
            "total_absent_days": total_absent_days,
            "present_percentage": present_percentage,
        },
    }

    return res, emp


async def create_employee(
    employee: EmployeeBase, created_by, mongo_client: AsyncIOMotorClient
):
    employee = employee.model_dump()

    employee["uuid"] = str(uuid.uuid4()).replace("-", "")

    password = await generate_random_password()

    employee["password"] = await hash_password(password)

    user = await create_user(employee, created_by, mongo_client)

    # TODO: Send email with password to employee and insist on changing it on first login

    emp_in_db = EmployeeInDB(**employee)

    emp_in_db.branch = emp_in_db.branch.value

    emp_in_db = emp_in_db.model_dump()

    if await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].insert_one(emp_in_db):
        emp_in_db["password"] = password
        return emp_in_db, user


async def create_user(employee: dict, created_by, mongo_client: AsyncIOMotorClient):
    primary_role = "employee"
    secondary_role = ["employee"]

    primary_role_doc = await mongo_client[MONGO_DATABASE][ROLES_COLLECTION].find_one(
        {"role": primary_role}
    )

    if not primary_role_doc:
        raise HTTPException(
            status_code=400, detail="Role '{}' does not exist".format(primary_role)
        )

    secondary_role_doc = []

    for role in secondary_role:
        role_doc = await mongo_client[MONGO_DATABASE][ROLES_COLLECTION].find_one(
            {"role": role}
        )

        if not role_doc:
            raise HTTPException(
                status_code=400, detail="Role '{}' does not exist".format(role)
            )

        secondary_role_doc.append(role_doc["_id"])

    user = UserBase(
        employee_id=employee["employee_id"],
        uuid=employee["uuid"],
        email=employee["email"],
        password=employee["password"],
        primary_role=primary_role_doc["_id"],
        secondary_roles=secondary_role_doc,
        created_by=created_by,
    )

    if await mongo_client[MONGO_DATABASE][USERS_COLLECTION].insert_one(
        user.model_dump()
    ):
        return user

    return None


async def get_employee(employee_id: str, mongo_client: AsyncIOMotorClient):
    emp = await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].find_one(
        {"employee_id": employee_id}, {"_id": 0}
    )

    if emp:
        return emp

    return None


async def get_employee_with_salary(
    employee_id: str, mongo_client: AsyncIOMotorClient, month=None
):
    if not month:
        # current_month = first_day_of_current_month()
        current_month = first_day_of_last_month()

    else:
        current_month = month

    # Change in pipeline should be done here
    pipeline = await pipelines.get_employee_with_salary_details(
        employee_id, current_month
    )

    emp = mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].aggregate(pipeline)

    data = [e async for e in emp]

    if len(data) == 1:
        return data[0]
    elif len(data) > 1:
        raise HTTPException(
            status_code=404,
            detail="Something went wrong, check get_employee function in crud/employees.py",
        )
    elif len(data) == 0:
        print("Employee not found")
        raise HTTPException(status_code=404, detail="Employee not found")

    return None


async def get_all_employees(mongo_client, **kwargs):
    branch = kwargs.get("branch", None)
    role = kwargs.get("role", None)

    pipeline = [
        {"$match": {"branch": branch}},
        {
            "$lookup": {
                "from": "users",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "user_info",
            }
        },
        {"$addFields": {"user_info": {"$arrayElemAt": ["$user_info", 0]}}},
        {
            "$lookup": {
                "from": "roles",
                "localField": "user_info.primary_role",
                "foreignField": "_id",
                "as": "primary_role",
            }
        },
        {"$addFields": {"primary_role": {"$arrayElemAt": ["$primary_role", 0]}}},
        {"$addFields": {"role": "$primary_role.role"}},
    ]
    project = {
        "_id": 0,
        "employee_id": 1,
        "name": 1,
        "email": 1,
    }
    if role:
        project.update({"role": 1})

    pipeline.append({"$project": project})

    emp = (
        await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION]
        .aggregate(pipeline)
        .to_list(None)
    )

    return emp


async def update_employee(employee_id: str, employee_details, mongo_client):
    update = await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].update_one(
        {"employee_id": employee_id}, {"$set": employee_details}
    )

    if update.matched_count == 1:
        return employee_details

    return None


async def delete_employee(employee_id, mongo_client):
    await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].delete_one(
        {"employee_id": employee_id}
    )

    await mongo_client[MONGO_DATABASE][USERS_COLLECTION].delete_one(
        {"employee_id": employee_id}
    )

    return True
