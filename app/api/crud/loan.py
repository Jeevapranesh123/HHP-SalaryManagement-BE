from app.database import AsyncIOMotorClient
from app.core.config import Config

from app.schemas.loan import LoanBase
from app.schemas.db import LoanInDB
from fastapi import HTTPException

import uuid
import datetime


MONGO_DATABASE = Config.MONGO_DATABASE
LOAN_COLLECTION = Config.LOAN_COLLECTION
LOAN_SCHEDULE_COLLECTION = Config.LOAN_SCHEDULE_COLLECTION


async def get_loan_history(employee_id, status, mongo_client: AsyncIOMotorClient):
    loan_history = (
        await mongo_client[MONGO_DATABASE][LOAN_COLLECTION]
        .find({"employee_id": employee_id}, {"_id": 0})
        .sort("requested_at", -1)
        .to_list(length=100)
    )

    if status:
        loan_history = list(filter(lambda x: x["status"] == status, loan_history))

    return loan_history


async def check_for_data_change(loan, new_data, mongo_client: AsyncIOMotorClient):
    new_amount = new_data.get("amount", None)
    new_tenure = new_data.get("tenure", None)
    new_emi = new_data.get("emi", None)

    amount_change = False
    tenure_change = False
    emi_change = False

    amount = None
    tenure = None
    emi = None

    if new_amount and loan["amount"] != new_amount:
        amount_change = True

    if new_tenure and loan["tenure"] != new_tenure:
        tenure_change = True

    if new_emi and loan["emi"] != new_emi:
        emi_change = True

    if amount_change and tenure_change and emi_change:
        raise HTTPException(
            status_code=400,
            detail="Amount, tenure and emi cannot be changed at the same time",
        )

    if amount_change and tenure_change:
        amount = new_amount
        tenure = new_tenure
        emi = amount / tenure
        change = True

    elif amount_change and emi_change:
        amount = new_amount
        emi = new_emi
        tenure = amount / emi if amount % emi == 0 else amount // emi + 1
        change = True

    elif tenure_change and emi_change:
        raise HTTPException(
            status_code=400,
            detail="Tenure and emi cannot be changed at the same time",
        )

    elif amount_change:
        raise HTTPException(
            status_code=400,
            detail="Amount cannot be changed",
        )

    elif tenure_change:
        tenure = new_tenure
        emi = (
            loan["amount"] / tenure
            if loan["amount"] % tenure == 0
            else loan["amount"] // tenure + 1
        )
        change = True

    elif emi_change:
        emi = new_emi
        tenure = (
            loan["amount"] / emi
            if loan["amount"] % emi == 0
            else loan["amount"] // emi + 1
        )
        change = True

    data_change = {}
    if amount:
        data_change["amount"] = amount
    if tenure:
        data_change["tenure"] = tenure
    if emi:
        data_change["emi"] = emi

    return data_change


async def get_next_month(date):
    if date.month == 12:
        return datetime.datetime(date.year + 1, 1, 1, 0, 0, 0)
    else:
        return datetime.datetime(date.year, date.month + 1, 1, 0, 0, 0)


async def get_loan(loan_id, mongo_client: AsyncIOMotorClient):
    loan = await mongo_client[MONGO_DATABASE][LOAN_COLLECTION].find_one(
        {"id": loan_id}, {"_id": 0}
    )
    if not loan:
        return None

    return loan


async def request_loan(
    loan: LoanBase, mongo_client: AsyncIOMotorClient, type: str, requester: str
):
    loan = loan.model_dump()

    loan["id"] = str(uuid.uuid4()).replace("-", "")
    loan["requested_by"] = requester
    loan["requested_at"] = datetime.datetime.now()
    loan["month"] = datetime.datetime.combine(loan["month"], datetime.time())

    if type == "request":
        loan["status"] = "pending"
    else:
        loan["status"] = "approved"
        loan["approved_or_rejected_by"] = requester
        loan["approved_or_rejected_at"] = datetime.datetime.now()

    loan_in_db = LoanInDB(**loan)

    if await mongo_client[MONGO_DATABASE][LOAN_COLLECTION].insert_one(
        loan_in_db.model_dump()
    ):
        return loan_in_db.model_dump()


async def respond_loan(loan_respond_req, mongo_client: AsyncIOMotorClient, responder):
    # FIXME: Move this logic to controller
    loan = await mongo_client[MONGO_DATABASE][LOAN_COLLECTION].find_one(
        {"id": loan_respond_req["loan_id"]}
    )

    if loan["status"] != "pending":
        raise HTTPException(
            status_code=400, detail="Loan has already been approved or rejected"
        )

    data_change = {
        "status": loan_respond_req["status"],
        "remarks": loan_respond_req["remarks"],
        "approved_or_rejected_by": responder,
        "approved_or_rejected_at": datetime.datetime.now(),
    }

    new_data = loan_respond_req.get("data_change", None)
    if new_data:
        new_data_change = await check_for_data_change(loan, new_data, mongo_client)
        data_change.update(new_data_change)

    update = await mongo_client[MONGO_DATABASE][LOAN_COLLECTION].find_one_and_update(
        {"id": loan_respond_req["loan_id"]},
        {"$set": data_change},
        return_document=True,
    )

    update["loan_id"] = update["id"]
    update.pop("_id")

    return update


async def build_repayment_schedule(loan, mongo_client: AsyncIOMotorClient):
    loan = await get_loan(loan["loan_id"], mongo_client)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan record not found")
    if loan["status"] != "approved":
        raise HTTPException(status_code=400, detail="Loan not approved yet")
    repayment_schedule = loan.get("repayment_schedule", None)
    if repayment_schedule:
        raise HTTPException(status_code=400, detail="Repayment schedule already built")

    repayment_schedule = []
    loan_amount = loan["amount"]
    loan_tenure = loan["tenure"]
    loan_emi = loan["emi"]
    month = loan["month"]
    for i in range(int(loan_tenure)):
        month = await get_next_month(month)
        repayment_schedule.append(
            {
                "employee_id": loan["employee_id"],
                "loan_id": loan["id"],
                "month": month,
                "amount": loan_emi if loan_amount > loan_emi else loan_amount,
            }
        )
        loan_amount -= loan_emi

    if await mongo_client[MONGO_DATABASE][LOAN_SCHEDULE_COLLECTION].insert_many(
        repayment_schedule
    ):
        for schedule in repayment_schedule:
            schedule.pop("_id")
            schedule["id"] = str(uuid.uuid4()).replace("-", "")
        await mongo_client[MONGO_DATABASE][LOAN_COLLECTION].update_one(
            {"id": loan["id"]}, {"$set": {"repayment_schedule": repayment_schedule}}
        )
        return True
