from fastapi import APIRouter, Depends, Response, Request
from app.database import get_mongo, AsyncIOMotorClient

from app.schemas.request import LoanCreateRequest, LoanRespondRequest

from app.api.controllers.loan import LoanController

router = APIRouter()


@router.post("/")
async def request_loan(
    LoanCreateRequest: LoanCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    payload = {"employee_id": "123", "primary_role": "employee"}
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.request_loan(LoanCreateRequest)


@router.post("/respond")
async def respond_loan(
    LoanRespondRequest: LoanRespondRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    payload = {"employee_id": "123", "primary_role": "employee"}
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.respond_loan(LoanRespondRequest, mongo_client)
