from app.database import AsyncIOMotorClient
from app.core.config import Config

from app.schemas.loan import LoanBase
from app.schemas.db import LoanInDB

import uuid
import datetime


MONGO_DATABASE = Config.MONGO_DATABASE
LOAN_COLLECTION = Config.LOAN_COLLECTION


async def get_next_month(date):
    if date.month == 12:
        return datetime.datetime(date.year + 1, 1, 1, 0, 0, 0)
    else:
        return datetime.datetime(date.year, date.month + 1, 1, 0, 0, 0)


async def request_loan(
    loan: LoanBase, mongo_client: AsyncIOMotorClient, type: str, requester: str
):
    loan = loan.model_dump()

    loan["id"] = str(uuid.uuid4()).replace("-", "")
    loan["requested_by"] = requester
    loan["requested_at"] = datetime.datetime.now()
    loan["month"] = datetime.datetime.combine(loan["month"], datetime.time())

    month = loan["month"]

    if type == "request":
        loan["status"] = "pending"
    else:
        loan["status"] = "approved"
        loan["approved_or_rejected_by"] = requester
        loan["approved_or_rejected_at"] = datetime.datetime.now()

    for i in range(loan["tenure"]):
        month = await get_next_month(month)
        d = {
            "employee_id": loan["employee_id"],
            "loan_id": loan["id"],
            "month": month,
        }
    total = loan["amount"]
    emi = loan["emi"]
    for i in range(loan["tenure"]):
        d["emi_" + str(i + 1)] = emi if total - emi > 0 else total
        total = total - emi if total - emi > 0 else 0
    print(d)

    return

    loan_in_db = LoanInDB(**loan)

    if await mongo_client[MONGO_DATABASE][LOAN_COLLECTION].insert_one(
        loan_in_db.model_dump()
    ):
        return loan_in_db


async def respond_loan(loan, mongo_client: AsyncIOMotorClient):
    loan = loan.model_dump()

    data_change = {
        "status": loan["status"],
        "remarks": loan["remarks"],
        "approved_or_rejected_at": datetime.datetime.now(),
    }

    if await mongo_client[MONGO_DATABASE][LOAN_COLLECTION].update_one(
        {"id": loan["loan_id"]},
        {"$set": data_change},
    ):
        return loan
