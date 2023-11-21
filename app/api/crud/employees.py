from app.schemas.employees import EmployeeBase
from app.schemas.db import EmployeeInDB
from app.schemas.request import EmployeeUpdateRequest
from app.database import AsyncIOMotorClient
from app.core.config import Config
from app.api.utils.employees import generate_random_password, hash_password
from app.schemas.auth import UserBase
import uuid
from fastapi import HTTPException


MONGO_DATABASE = Config.MONGO_DATABASE
EMPLOYEE_COLLECTION = Config.EMPLOYEE_COLLECTION
USERS_COLLECTION = Config.USERS_COLLECTION
ROLES_COLLECTION = Config.ROLES_COLLECTION


async def create_employee(employee: EmployeeBase, mongo_client: AsyncIOMotorClient):
    employee = employee.model_dump()

    employee["uuid"] = str(uuid.uuid4()).replace("-", "")

    # password = generate_random_password()

    password = "string"
    employee["password"] = await hash_password(password)

    print(password)

    await create_user(
        employee,
        mongo_client,
    )

    # TODO: Send email with password to employee and insist on changing it on first login

    emp_in_db = EmployeeInDB(**employee)

    if await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].insert_one(
        emp_in_db.model_dump()
    ):
        res = emp_in_db.model_dump()
        res["password"] = password
        return res


async def create_user(employee: dict, mongo_client: AsyncIOMotorClient):
    role = "employee"

    rolesdoc = await mongo_client[MONGO_DATABASE][ROLES_COLLECTION].find_one(
        {"role": role}
    )

    if not rolesdoc:
        raise HTTPException(
            status_code=400, detail="Role '{}' does not exist".format(role)
        )

    user = UserBase(
        employee_id=employee["employee_id"],
        uuid=employee["uuid"],
        email=employee["email"],
        password=employee["password"],
        roles=[rolesdoc["_id"]],
    )

    if await mongo_client[MONGO_DATABASE][USERS_COLLECTION].insert_one(
        user.model_dump()
    ):
        return user

    return None


async def get_employee(employee_id: str, mongo_client: AsyncIOMotorClient):
    pipeline = [
        {
            "$match": {
                "employee_id": employee_id,
            }
        },
        {
            "$lookup": {
                "from": "salary",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "salary_info",
            }
        },
        {
            "$lookup": {
                "from": "temp_salary",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "temp_salary_info",
            }
        },
        {
            "$addFields": {
                "salary": {"$arrayElemAt": ["$salary_info", 0]},
                "temp_salary": {"$arrayElemAt": ["$temp_salary_info", 0]},
            }
        },
        {
            "$addFields": {
                "gross_salary": "$salary.gross",
                "pf": "$salary.pf",
                "esi": "$salary.esi",
                "loss_of_pay": "$temp_salary.loss_of_pay",
                "attendance_special_allowance": "$temp_salary.attendance_special_allowance",
                "leave_cashback": "$temp_salary.leave_cashback",
                "last_year_leave_cashback": "$temp_salary.last_year_leave_cashback",
            }
        },
        {
            "$project": {
                "temp_salary_info": 0,
                "salary_info": 0,
                "salary": 0,
                "temp_salary": 0,
                "_id": 0,
            }
        },
        {
            "$addFields": {
                "net_salary": {
                    "$subtract": [
                        {
                            "$add": [
                                "$gross_salary",
                                "$attendance_special_allowance",
                                "$leave_cashback",
                                "$last_year_leave_cashback",
                            ]
                        },
                        {"$add": ["$pf", "$esi", "$loss_of_pay"]},
                    ]
                }
            }
        },
    ]

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
        raise HTTPException(status_code=404, detail="Employee not found")

    return None


async def get_all_employees(mongo_client):
    emps = mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].find(
        {}, {"employee_id": 1, "name": 1, "email": 1, "_id": 0}
    )

    return [e async for e in emps]


async def update_employee(employee_id: str, employee_details, mongo_client):
    if await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].update_one(
        {"employee_id": employee_id}, {"$set": employee_details}
    ):
        return await get_employee(employee_id, mongo_client)

    return None
