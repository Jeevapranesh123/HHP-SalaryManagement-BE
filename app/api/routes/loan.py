from fastapi import APIRouter, Depends, Response, Request
from app.database import get_mongo, AsyncIOMotorClient

from app.schemas.request import LoanCreateRequest, LoanRespondRequest

from app.api.controllers import loan as loan_controller

router = APIRouter()


@router.post("/")
async def request_loan(
    LoanCreateRequest: LoanCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await loan_controller.request_loan(LoanCreateRequest, mongo_client)


@router.post("/respond")
async def respond_loan(
    LoanRespondRequest: LoanRespondRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await loan_controller.respond_loan(LoanRespondRequest, mongo_client)
