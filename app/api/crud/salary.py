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


async def get_salary_advance_history(
    employee_id, status, mongo_client: AsyncIOMotorClient
):
    salary_advance_history = (
        await mongo_client[MONGO_DATABASE][SALARY_ADVANCE_COLLECTION]
        .find({"employee_id": employee_id}, {"_id": 0})
        .sort("requested_at", -1)
        .to_list(length=100)
    )

    if status:
        salary_advance_history = list(
            filter(lambda x: x["status"] == status, salary_advance_history)
        )

    return salary_advance_history


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
    salary_advance, mongo_client: AsyncIOMotorClient, type: str, requester: str
):
    salary = salary_advance
    salary["id"] = str(uuid.uuid4()).replace("-", "")

    salary["requested_by"] = requester
    salary["requested_at"] = datetime.datetime.now()

    salary["month"] = datetime.datetime.combine(salary["month"], datetime.time())

    if type == "request":
        salary["status"] = "pending"
        salary["remarks"] = ""
    elif type == "post":
        salary["status"] = "approved"
        salary["approved_or_rejected_by"] = requester
        salary["approved_or_rejected_at"] = datetime.datetime.now()
    else:
        raise HTTPException(status_code=400, detail="Invalid Request Type")

    salary_advance_in_db = SalaryAdvanceInDB(**salary)

    if await mongo_client[MONGO_DATABASE][SALARY_ADVANCE_COLLECTION].insert_one(
        salary_advance_in_db.model_dump()
    ):
        return salary_advance_in_db.model_dump()


async def respond_salary_advance(salary, mongo_client: AsyncIOMotorClient):
    already_approved_or_rejected = await mongo_client[MONGO_DATABASE][
        SALARY_ADVANCE_COLLECTION
    ].find_one({"id": salary["salary_advance_id"], "status": {"$ne": "pending"}})

    if already_approved_or_rejected:
        raise HTTPException(
            status_code=400,
            detail="Salary Advance has already been approved or rejected",
        )

    new_data = salary.get("data_change", None)

    data_change = {
        "status": salary["status"],
        "remarks": salary["remarks"],
        "approved_or_rejected_at": datetime.datetime.now(),
    }
    change = False
    if new_data:
        update = await mongo_client[MONGO_DATABASE][
            SALARY_ADVANCE_COLLECTION
        ].update_one(
            {"id": salary["salary_advance_id"]},
            {"$set": new_data},
        )
        if update.modified_count == 1:
            change = True
            # FIXME: Notify the employee regarding the change in amount or month
            pass

    update = await mongo_client[MONGO_DATABASE][
        SALARY_ADVANCE_COLLECTION
    ].find_one_and_update(
        {"id": salary["salary_advance_id"]}, {"$set": data_change}, return_document=True
    )

    update["salary_advance_id"] = update["id"]
    update.pop("_id")
    if change:
        update["data_changed"] = True
    return update

    # FIXME: If not update decide the response


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


async def get_salary_advance(salary_advance_id: str, mongo_client: AsyncIOMotorClient):
    data = await mongo_client[MONGO_DATABASE][SALARY_ADVANCE_COLLECTION].find_one(
        {"id": salary_advance_id}, {"_id": 0}
    )
    if not data:
        return None

    return data
