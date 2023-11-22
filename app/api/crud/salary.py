from app.database import AsyncIOMotorClient
from fastapi import HTTPException
from app.core.config import Config

from app.schemas.salary import (
    SalaryBase,
    SalaryAdvanceBase,
    MonthlyCompensationBase,
    SalaryIncentivesBase,
)
from app.schemas.db import (
    SalaryInDB,
    SalaryAdvanceInDB,
    MonthlyCompensationInDB,
    SalaryIncentivesInDB,
)

import uuid
import datetime

MONGO_DATABASE = Config.MONGO_DATABASE
SALARY_COLLECTION = Config.SALARY_COLLECTION
MONTHLY_COMPENSATION_COLLECTION = Config.MONTHLY_COMPENSATION_COLLECTION
SALARY_INCENTIVES_COLLECTION = Config.SALARY_INCENTIVES_COLLECTION
LOAN_COLLECTION = Config.LOAN_COLLECTION
SALARY_ADVANCE_COLLECTION = Config.SALARY_ADVANCE_COLLECTION


async def get_all_salaries(mongo_client: AsyncIOMotorClient):
    return (
        await mongo_client[MONGO_DATABASE][SALARY_COLLECTION]
        .find({}, {"_id": 0})
        .to_list(None)
    )


async def create_salary(SalaryBase: SalaryBase, mongo_client: AsyncIOMotorClient):
    dict_salary = SalaryBase.model_dump()
    dict_salary["id"] = str(uuid.uuid4()).replace("-", "")

    salary_in_db = SalaryInDB(**dict_salary)

    if await mongo_client[MONGO_DATABASE][SALARY_COLLECTION].insert_one(
        salary_in_db.model_dump()
    ):
        return salary_in_db


async def create_monthly_compensation(
    MonthlyCompensationBase: MonthlyCompensationBase, mongo_client: AsyncIOMotorClient
):
    dict_salary = MonthlyCompensationBase.model_dump()
    dict_salary["id"] = str(uuid.uuid4()).replace("-", "")

    salary_in_db = MonthlyCompensationInDB(**dict_salary)

    if await mongo_client[MONGO_DATABASE][MONTHLY_COMPENSATION_COLLECTION].insert_one(
        salary_in_db.model_dump()
    ):
        return salary_in_db


async def create_salary_incentives(
    SalaryIncentivesBase: SalaryIncentivesBase, mongo_client: AsyncIOMotorClient
):
    dict_salary = SalaryIncentivesBase.model_dump()
    dict_salary["id"] = str(uuid.uuid4()).replace("-", "")

    salary_in_db = SalaryIncentivesInDB(**dict_salary)

    if await mongo_client[MONGO_DATABASE][SALARY_INCENTIVES_COLLECTION].insert_one(
        salary_in_db.model_dump()
    ):
        return salary_in_db


async def request_advance(
    SalaryAdvanceRequest: SalaryAdvanceBase, mongo_client: AsyncIOMotorClient
):
    salary = SalaryAdvanceRequest.model_dump()
    salary["id"] = str(uuid.uuid4()).replace("-", "")
    salary_advance_in_db = SalaryAdvanceInDB(**salary)

    if await mongo_client[MONGO_DATABASE][SALARY_ADVANCE_COLLECTION].insert_one(
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
    data = await mongo_client[MONGO_DATABASE][SALARY_COLLECTION].find_one(
        {"employee_id": employee_id}, {"_id": 0}
    )
    if not data:
        return None

    return data


async def update_salary(
    SalaryCreateRequest: SalaryBase, mongo_client: AsyncIOMotorClient, updated_by: str
):
    salary = SalaryCreateRequest.model_dump(exclude_none=True)

    employee_id = salary.pop("employee_id")
    salary["updated_by"] = updated_by
    salary["updated_at"] = datetime.datetime.now()

    existing_salary = await mongo_client[MONGO_DATABASE][SALARY_COLLECTION].find_one(
        {"employee_id": employee_id}, {"_id": 0}
    )

    if not existing_salary:
        salary["created_at"] = datetime.datetime.now()

    if await mongo_client[MONGO_DATABASE][SALARY_COLLECTION].update_one(
        {"employee_id": employee_id},
        {"$set": salary},
        upsert=True,
    ):
        salary["employee_id"] = employee_id
        return salary


async def update_monthly_compensation(
    MonthlyCompensationBase: MonthlyCompensationBase,
    mongo_client: AsyncIOMotorClient,
    updated_by: str,
):
    salary = MonthlyCompensationBase.model_dump(exclude_none=True)

    employee_id = salary.pop("employee_id")
    salary["updated_by"] = updated_by
    salary["updated_at"] = datetime.datetime.now()

    existing_salary = await mongo_client[MONGO_DATABASE][
        MONTHLY_COMPENSATION_COLLECTION
    ].find_one({"employee_id": employee_id}, {"_id": 0})

    if not existing_salary:
        salary["created_at"] = datetime.datetime.now()

    if await mongo_client[MONGO_DATABASE][MONTHLY_COMPENSATION_COLLECTION].update_one(
        {"employee_id": employee_id},
        {"$set": salary},
        upsert=True,
    ):
        salary["employee_id"] = employee_id
        return salary


async def update_salary_incentives(
    SalaryIncentivesBase: SalaryIncentivesBase,
    mongo_client: AsyncIOMotorClient,
    updated_by: str,
):
    salary = SalaryIncentivesBase.model_dump(exclude_none=True)

    employee_id = salary.pop("employee_id")
    salary["updated_by"] = updated_by
    salary["updated_at"] = datetime.datetime.now()

    existing_salary = await mongo_client[MONGO_DATABASE][
        SALARY_INCENTIVES_COLLECTION
    ].find_one({"employee_id": employee_id}, {"_id": 0})

    if not existing_salary:
        salary["created_at"] = datetime.datetime.now()

    if await mongo_client[MONGO_DATABASE][SALARY_INCENTIVES_COLLECTION].update_one(
        {"employee_id": employee_id},
        {"$set": salary},
        upsert=True,
    ):
        salary["employee_id"] = employee_id
        return salary
