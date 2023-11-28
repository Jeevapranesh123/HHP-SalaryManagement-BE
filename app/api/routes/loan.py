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

from app.schemas.employees import StatusEnum


router = APIRouter()


@router.get("/meta")
async def get_meta(
    access_type: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_respond_action = [
        {
            "label": "Approve",
            "type": "button",
            "variant": "success",
            "action": {"url": "/loan/respond", "method": "POST"},
            "body": {"status": "approved"},
        },
        {
            "label": "Reject",
            "type": "button",
            "variant": "destructive",
            "action": {"url": "/loan/respond", "method": "POST"},
            "body": {"status": "rejected"},
        },
    ]

    loan_post_action = [
        {
            "label": "Submit",
            "type": "button",
            "variant": "default",
            "action": {"url": "/loan", "method": "POST"},
        }
    ]

    loan_request_action = [
        {
            "label": "Request",
            "type": "button",
            "variant": "default",
            "action": {"url": "/loan/request", "method": "POST"},
        }
    ]

    data = {
        "message": "Loan meta fetched successfully",
        "status_code": 200,
        "data": {
            "type": {
                "loan": {
                    "data": {
                        "employee_id": {"type": "string", "value": 0, "required": True},
                        "amount": {"type": "number", "value": 0, "required": True},
                        "month": {
                            "type": "month",
                            "format": "YYYY-MM-DD",
                            "required": True,
                        },
                        "payback_type": {
                            "type": "dropdown",
                            "options": [
                                {"label": "EMI", "value": "emi"},
                                {"label": "Tenure", "value": "tenure"},
                            ],
                            "required": True,
                        },
                        "payback_value": {
                            "type": "number",
                            "value": 0,
                            "required": True,
                        },
                        "remarks": {"type": "textarea", "value": "", "required": True},
                    }
                },
            }
        },
    }

    if access_type == "request":
        data["data"]["type"]["loan"]["actions"] = loan_request_action
        data["data"]["type"]["loan"]["data"].pop("remarks")
    elif access_type == "respond":
        data["data"]["type"]["loan"]["actions"] = loan_respond_action
        data["data"]["type"]["loan"]["data"]["employee_id"]["editable"] = False
        data["data"]["type"]["loan"]["data"]["payback_type"]["editable"] = False

    elif access_type == "post":
        data["data"]["type"]["loan"]["actions"] = loan_post_action

    return data


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


@router.post("/adjust")
@role_required(["MD"])
async def adjust_loan(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.adjust_loan(LoanRespondRequest)
    return LoanRespondResponse(
        message="Loan adjusted successfully",
        status_code=200,
        data=res,
    )


@router.get("/history")
async def get_loan_history(
    employee_id: str,
    status: StatusEnum = None,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    if status and status.value == "all":
        status = None
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.get_loan_history(employee_id, status)

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
