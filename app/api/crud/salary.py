from app.database import AsyncIOMotorClient
from app.core.config import Config

from app.schemas.salary import SalaryBase, SalaryAdvanceBase
from app.schemas.db import SalaryInDB, SalaryAdvanceInDB

import uuid
import datetime

MONGO_DATABASE = Config.MONGO_DATABASE
SALARY_COLLECTION = Config.SALARY_COLLECTION
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
    salary_in_db = SalaryInDB(**SalaryCreateRequest.model_dump())

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
