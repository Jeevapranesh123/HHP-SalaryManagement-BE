from fastapi import APIRouter, Depends, Response, Request
from app.database import get_mongo, AsyncIOMotorClient

from app.schemas.request import (
    LoanCreateRequest,
    LoanRespondRequest,
    LoanAdjustmentRequest,
)

from app.api.controllers.loan import LoanController

from app.api.utils.employees import verify_login_token
from app.api.utils.auth import role_required

from app.schemas.response import (
    PostLoanResponse,
    RequestLoanResponse,
    LoanRespondResponse,
    LoanResponse,
    LoanHistoryResponse,
    GetRepaymentRecordResponse,
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
                        "emi": {"type": "number", "value": 0, "required": True},
                        "tenure": {"type": "number", "value": 0, "required": True},
                        "remarks": {"type": "textarea", "value": "", "required": True},
                    }
                },
            }
        },
    }

    if access_type == "request":
        data["data"]["type"]["loan"]["actions"] = loan_request_action
        data["data"]["type"]["loan"]["data"].pop("remarks")
        data["data"]["type"]["loan"]["data"].pop("emi")
        data["data"]["type"]["loan"]["data"].pop("tenure")
        data["data"]["type"]["loan"]["data"]["employee_id"]["editable"] = False

    elif access_type == "respond":
        data["data"]["type"]["loan"]["actions"] = loan_respond_action
        data["data"]["type"]["loan"]["data"]["employee_id"]["editable"] = False
        data["data"]["type"]["loan"]["data"]["month"]["editable"] = False
        data["data"]["type"]["loan"]["data"]["tenure"]["editable"] = False

        data["data"]["type"]["loan"]["data"].pop("payback_type")
        data["data"]["type"]["loan"]["data"].pop("payback_value")

    elif access_type == "post":
        data["data"]["type"]["loan"]["actions"] = loan_post_action
        data["data"]["type"]["loan"]["data"]["employee_id"]["editable"] = False
        data["data"]["type"]["loan"]["data"].pop("emi")
        data["data"]["type"]["loan"]["data"].pop("tenure")

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


@router.get("/repayment/schedule/{loan_id}")
async def get_repayment_schedule(
    loan_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.get_repayment_schedule(loan_id)

    return {
        "message": "Repayment schedule fetched successfully",
        "status_code": 200,
        "data": res,
    }


@router.get("/repayment/emi/{repayment_id}")
async def get_repayment_emi(
    repayment_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.get_repayment_emi(repayment_id)

    return GetRepaymentRecordResponse(
        message="Repayment record fetched successfully",
        status_code=200,
        data=res,
    )


@router.get("/adjust/meta")
async def get_loan_adjust_meta(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.get_loan_adjust_meta()

    return {
        "message": "Adjustment meta fetched successfully",
        "status_code": 200,
        "data": res,
    }


@router.post("/adjust")
@role_required(["MD"])
async def adjust_loan(
    loan_adjustment: LoanAdjustmentRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    loan_controller = LoanController(payload, mongo_client)
    res = await loan_controller.adjust_loan(loan_adjustment)
    return res
    # return LoanRespondResponse(
    #     message="Loan adjusted successfully",
    #     status_code=200,
    #     data=res,
    # )


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
