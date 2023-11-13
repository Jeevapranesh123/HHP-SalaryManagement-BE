from app.database import AsyncIOMotorClient
from fastapi import HTTPException
from app.core.config import Config

from app.schemas.salary import SalaryBase, SalaryAdvanceBase
from app.schemas.db import SalaryInDB, SalaryAdvanceInDB

import uuid
import datetime

MONGO_DATABASE = Config.MONGO_DATABASE
SALARY_COLLECTION = Config.SALARY_COLLECTION
TEMP_SALARY_COLLECTION = Config.TEMP_SALARY_COLLECTION
LOAN_COLLECTION = Config.LOAN_COLLECTION


async def get_all_salaries(mongo_client: AsyncIOMotorClient):
    return (
        await mongo_client[MONGO_DATABASE][SALARY_COLLECTION]
        .find({}, {"_id": 0})
        .to_list(None)
    )


async def create_salary(
    SalaryCreateRequest: SalaryBase, mongo_client: AsyncIOMotorClient
):
    dict_salary = SalaryCreateRequest.model_dump()
    # dict_salary["net_salary"] = (
    #     dict_salary["gross"] - dict_salary["pf"] - dict_salary["esi"]
    # )
    dict_salary["id"] = str(uuid.uuid4()).replace("-", "")

    salary_in_db = SalaryInDB(**dict_salary)

    if await mongo_client[MONGO_DATABASE][SALARY_COLLECTION].insert_one(
        salary_in_db.model_dump()
    ):
        return salary_in_db


async def request_advance(
    SalaryAdvanceRequest: SalaryAdvanceBase, mongo_client: AsyncIOMotorClient
):
    salary = SalaryAdvanceRequest.model_dump()
    salary["id"] = str(uuid.uuid4()).replace("-", "")
    salary_advance_in_db = SalaryAdvanceInDB(**salary)

    if await mongo_client[MONGO_DATABASE][LOAN_COLLECTION].insert_one(
        salary_advance_in_db.model_dump()
    ):
        return salary_advance_in_db


async def respond_salary_advance(salary, mongo_client: AsyncIOMotorClient):
    salary = salary.model_dump()

    data_change = {
        "status": salary["status"],
        "remarks": salary["remarks"],
        "approved_or_rejected_at": datetime.datetime.now(),
    }

    if await mongo_client[MONGO_DATABASE][LOAN_COLLECTION].update_one(
        {"id": salary["salary_advance_id"]},
        {"$set": data_change},
    ):
        return salary


async def get_salary(employee_id: str, mongo_client: AsyncIOMotorClient):
    return await mongo_client[MONGO_DATABASE][SALARY_COLLECTION].find_one(
        {"employee_id": employee_id}, {"_id": 0}
    )


async def update_salary(
    SalaryCreateRequest: SalaryBase, mongo_client: AsyncIOMotorClient
):
    salary = SalaryCreateRequest.model_dump()

    data_change = {
        "gross": salary["gross"],
        "pf": salary["pf"],
        "esi": salary["esi"],
        # "net_salary": salary["gross"] - salary["pf"] - salary["esi"],
        "updated_at": datetime.datetime.now(),
    }

    existing_salary = await mongo_client[MONGO_DATABASE][SALARY_COLLECTION].find_one(
        {"employee_id": salary["employee_id"]}, {"_id": 0}
    )

    if not existing_salary:
        raise HTTPException(status_code=400, detail="Salary does not exist")

    if await mongo_client[MONGO_DATABASE][SALARY_COLLECTION].update_one(
        {"employee_id": salary["employee_id"]},
        {"$set": data_change},
    ):
        return salary


async def create_temp(temp: dict, mongo_client: AsyncIOMotorClient):
    temp = temp.model_dump()
    temp["id"] = str(uuid.uuid4()).replace("-", "")
    temp["created_at"] = datetime.datetime.now()
    temp["updated_at"] = datetime.datetime.now()

    if await mongo_client[MONGO_DATABASE][TEMP_SALARY_COLLECTION].update_one(
        {"employee_id": temp["employee_id"]}, {"$set": temp}, upsert=True
    ):
        return temp
