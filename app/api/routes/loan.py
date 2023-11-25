from fastapi import APIRouter, Depends, Response, Request
from app.database import get_mongo, AsyncIOMotorClient

from app.schemas.request import LoanCreateRequest, LoanRespondRequest

from app.api.controllers.loan import LoanController

from app.api.utils.employees import verify_login_token
from app.api.utils.auth import role_required

from app.schemas.response import (
    PostLoanResponse,
    RequestLoanResponse,
    LoanRespondResponse,
    LoanResponse,
    LoanHistoryResponse,
)


router = APIRouter()


@router.post("/")
@role_required(["MD"])
async def post_loan(
    LoanCreateRequest: LoanCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.post_loan(LoanCreateRequest)
    return PostLoanResponse(
        message="Loan posted successfully",
        status_code=200,
        data=res,
    )


@router.post("/request")
async def request_loan(
    LoanCreateRequest: LoanCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.request_loan(LoanCreateRequest)
    return RequestLoanResponse(
        message="Loan requested successfully",
        status_code=200,
        data=res,
    )


@router.post("/respond")
@role_required(["MD"])
async def respond_loan(
    LoanRespondRequest: LoanRespondRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.respond_loan(LoanRespondRequest)
    return LoanRespondResponse(
        message="Loan responded successfully",
        status_code=200,
        data=res,
    )


@router.get("/history")
async def get_loan_history(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.get_loan_history(employee_id)

    return LoanHistoryResponse(
        message="Loan history fetched successfully",
        status_code=200,
        data=res,
    )


@router.get("/{loan_id}")
async def get_loan(
    loan_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.get_loan(loan_id)

    return {
        "message": "Loan fetched successfully",
        "status_code": 200,
        "data": LoanResponse(**res),
    }
