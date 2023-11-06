from app.database import AsyncIOMotorClient
from app.core.config import Config

from app.schemas.loan import LoanBase
from app.schemas.db import LoanInDB

import uuid
import datetime


MONGO_DATABASE = Config.MONGO_DATABASE
LOAN_COLLECTION = Config.LOAN_COLLECTION


async def request_loan(loan: LoanBase, mongo_client: AsyncIOMotorClient):
    loan = loan.model_dump()

    print(loan)

    loan["id"] = str(uuid.uuid4()).replace("-", "")

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
