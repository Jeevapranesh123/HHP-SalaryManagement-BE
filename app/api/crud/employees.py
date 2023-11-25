from app.schemas.employees import EmployeeBase
from app.schemas.db import EmployeeInDB
from app.schemas.request import EmployeeUpdateRequest
from app.database import AsyncIOMotorClient
from app.core.config import Config
from app.api.utils.employees import generate_random_password, hash_password
from app.schemas.auth import UserBase
import uuid
from fastapi import HTTPException
from datetime import datetime, timezone


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

    await create_user(employee, mongo_client)

    # TODO: Send email with password to employee and insist on changing it on first login

    emp_in_db = EmployeeInDB(**employee)

    if await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].insert_one(
        emp_in_db.model_dump()
    ):
        res = emp_in_db.model_dump()
        res["password"] = password
        return res


async def create_user(employee: dict, mongo_client: AsyncIOMotorClient):
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


async def get_employee_with_salary(employee_id: str, mongo_client: AsyncIOMotorClient):
    current_month = datetime.now(tz=timezone.utc).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

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
                "from": "monthly_compensation",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "monthly_compensation_info",
                "let": {"employee_id": "$employee_id", "targetDate": current_month},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$employee_id", "$$employee_id"]},
                                    {"$eq": ["$month", "$$targetDate"]},
                                ]
                            }
                        }
                    }
                ],
            }
        },
        {
            "$lookup": {
                "from": "loan_schedule",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "loan_schedule_info",
                "let": {"employee_id": "$employee_id", "targetMonth": current_month},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$employee_id", "$$employee_id"]},
                                    {"$eq": ["$month", "$$targetMonth"]},
                                ]
                            }
                        }
                    },
                    {"$group": {"_id": "$month", "sum": {"$sum": "$amount"}}},
                ],
            }
        },
        {
            "$lookup": {
                "from": "salary_advance",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "salary_advance_info",
                "let": {"employeeId": "$employee_id", "targetDate": current_month},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$employee_id", "$$employeeId"]},
                                    {"$eq": ["$month", "$$targetDate"]},
                                    {"$eq": ["$status", "approved"]},
                                ]
                            }
                        }
                    },
                    {"$group": {"_id": "$month", "sum": {"$sum": "$amount"}}},
                ],
            }
        },
        {
            "$lookup": {
                "from": "salary_incentives",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "salary_incentives_info",
                "let": {"employeeId": "$employee_id", "targetDate": current_month},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$employee_id", "$$employeeId"]},
                                    {"$eq": ["$month", "$$targetDate"]},
                                ]
                            }
                        }
                    }
                ],
            }
        },
        {
            "$addFields": {
                "salary": {"$arrayElemAt": ["$salary_info", 0]},
                "monthly_compensation": {
                    "$arrayElemAt": ["$monthly_compensation_info", 0]
                },
                "salary_advance": {"$arrayElemAt": ["$salary_advance_info", 0]},
                "loan": {"$arrayElemAt": ["$loan_schedule_info", 0]},
                "salary_incentives": {"$arrayElemAt": ["$salary_incentives_info", 0]},
            }
        },
        {
            "$addFields": {
                "gross_salary": {"$ifNull": ["$salary.gross_salary", 0]},
                "pf": {"$ifNull": ["$salary.pf", 0]},
                "esi": {"$ifNull": ["$salary.esi", 0]},
                "loss_of_pay": {"$ifNull": ["$monthly_compensation.loss_of_pay", 0]},
                "leave_cashback": {
                    "$ifNull": ["$monthly_compensation.leave_cashback", 0]
                },
                "last_year_leave_cashback": {
                    "$ifNull": ["$monthly_compensation.last_year_leave_cashback", 0]
                },
                "attendance_special_allowance": {
                    "$ifNull": ["$monthly_compensation.attendance_special_allowance", 0]
                },
                "other_special_allowance": {
                    "$ifNull": ["$monthly_compensation.other_special_allowance", 0]
                },
                "overtime": {"$ifNull": ["$monthly_compensation.overtime", 0]},
                "salary_advance": {"$ifNull": ["$salary_advance.sum", 0]},
                "loan": {"$ifNull": ["$loan.sum", 0]},
                "allowance": {"$ifNull": ["$salary_incentives.allowance", 0]},
                "increment": {"$ifNull": ["$salary_incentives.increment", 0]},
                "bonus": {"$ifNull": ["$salary_incentives.bonus", 0]},
            }
        },
        {
            "$project": {
                "salary_info": 0,
                "monthly_compensation_info": 0,
                "salary_incentives_info": 0,
                "salary": 0,
                "monthly_compensation": 0,
                "salary_incentives": 0,
                "loan_schedule_info": 0,
                "salary_advance_info": 0,
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
                                "$other_special_allowance",
                                "$overtime",
                                "$allowance",
                                "$increment",
                                "$bonus",
                            ]
                        },
                        {
                            "$add": [
                                "$pf",
                                "$esi",
                                "$loss_of_pay",
                                "$salary_advance",
                                "$loan",
                            ]
                        },
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
        print("Employee not found")
        raise HTTPException(status_code=404, detail="Employee not found")

    return None


async def get_all_employees(mongo_client):
    emps = mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].find(
        {}, {"employee_id": 1, "name": 1, "email": 1, "_id": 0}
    )

    return [e async for e in emps]


async def update_employee(employee_id: str, employee_details, mongo_client):
    update = await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].update_one(
        {"employee_id": employee_id}, {"$set": employee_details}
    )

    if update.matched_count == 1:
        return employee_details

    return None
