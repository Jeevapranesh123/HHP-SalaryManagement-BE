from fastapi import APIRouter, Depends, Response, Request


# import DB Utils
from app.database import get_mongo, AsyncIOMotorClient

from app.api.controllers.salary import SalaryController

from app.schemas.request import (
    PostSalaryRequest,
    PostMonthlyCompensationRequest,
    PostSalaryIncentivesRequest,
    SalaryAdvanceRequest,
    SalaryAdvanceRespondRequest,
)

# FIXME: Create a Request and Response Schema for Temp Salary
from app.schemas.response import (
    PostSalaryResponse,
    PostMonthlyCompensationResponse,
    PostSalaryIncentivesResponse,
    PostSalaryAdvanceResponse,
    RequestSalaryAdvanceResponse,
    SalaryAdvanceRespondResponse,
)
from app.schemas.employees import StatusEnum
from app.api.utils.employees import verify_login_token

router = APIRouter()


@router.get("/", status_code=200)
async def get_all_salaries(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    return await sal_obj.get_all_salaries()


@router.get("/get_salary/{employee_id}", status_code=200)
async def get_salary(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.get_salary(employee_id)
    return {
        "message": "Salary fetched successfully",
        "status_code": 200,
        "data": res,
    }


@router.get("/history/{employee_id}", status_code=200)
async def get_salary_history(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.get_salary_history(employee_id)
    return {
        "message": "Salary fetched successfully",
        "status_code": 200,
        "data": res,
    }


@router.put("/post_salary")
async def post_salary(
    PostSalaryRequest: PostSalaryRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.post_salary(PostSalaryRequest)

    return PostSalaryResponse(
        message="Salary Updated successfully",
        status_code=200,
        data=res,
    )


@router.get("/monthly_compensation/history/{employee_id}", status_code=200)
async def get_monthly_compensation_history(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.get_monthly_compensation_history(employee_id)
    return {
        "message": "Monthly Compensation fetched successfully",
        "status_code": 200,
        "data": res,
    }


@router.put("/post_monthly_compensation")
async def post_monthly_compensation(
    PostMonthlyCompensationRequest: PostMonthlyCompensationRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.post_monthly_compensation(PostMonthlyCompensationRequest)

    return PostMonthlyCompensationResponse(
        message="Monthly Compensation Updated successfully",
        status_code=200,
        data=res,
    )


@router.get("/salary_incentives/history/{employee_id}", status_code=200)
async def get_salary_incentives_history(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.get_salary_incentives_history(employee_id)
    return {
        "message": "Salary Incentives fetched successfully",
        "status_code": 200,
        "data": res,
    }


@router.put("/post_salary_incentives")
async def post_salary_incentives(
    PostSalaryIncentivesRequest: PostSalaryIncentivesRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.post_salary_incentives(PostSalaryIncentivesRequest)

    return PostSalaryIncentivesResponse(
        message="Salary Incentives Updated successfully",
        status_code=200,
        data=res,
    )


@router.get("/advance/meta")
async def get_meta(
    access_type: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    advance_request_action = [
        {
            "label": "Request",
            "type": "button",
            "variant": "default",
            "action": {"url": "/salary/advance/request", "method": "POST"},
        }
    ]

    advance_respond_action = [
        {
            "label": "Approve",
            "type": "button",
            "variant": "success",
            "action": {"url": "/salary/advance/respond", "method": "POST"},
            "body": {"status": "approved"},
        },
        {
            "label": "Reject",
            "type": "button",
            "variant": "destructive",
            "action": {"url": "/salary/advance/respond", "method": "POST"},
            "body": {"status": "rejected"},
        },
    ]

    advance_post_action = [
        {
            "label": "Submit",
            "type": "button",
            "variant": "default",
            "action": {"url": "/salary/advance", "method": "POST"},
        }
    ]
    data = {
        "message": "Salary meta fetched successfully",
        "status_code": 200,
        "data": {
            "salary_advance": {
                "data": {
                    "employee_id": {
                        "type": "string",
                        "required": True,
                    },
                    "amount": {"type": "number", "value": 0, "required": True},
                    "month": {
                        "type": "month",
                        "format": "YYYY-MM-DD",
                        "required": True,
                    },
                    "remarks": {"type": "textarea", "value": "", "required": True},
                },
            }
        },
    }

    if access_type == "request":
        data["data"]["salary_advance"]["actions"] = advance_request_action
        data["data"]["salary_advance"]["data"].pop("remarks")
        data["data"]["salary_advance"]["data"]["employee_id"]["editable"] = False

    elif access_type == "respond":
        data["data"]["salary_advance"]["actions"] = advance_respond_action
        data["data"]["salary_advance"]["data"]["employee_id"]["editable"] = False
        # data["data"]["salary_advance"]["data"]["month"]["editable"] = False

    elif access_type == "post":
        data["data"]["salary_advance"]["actions"] = advance_post_action
        data["data"]["salary_advance"]["data"]["employee_id"]["editable"] = False

    return data


@router.post("/advance")
async def post_advance(
    SalaryAdvanceRequest: SalaryAdvanceRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.post_advance(SalaryAdvanceRequest)
    return PostSalaryAdvanceResponse(
        message="Salary Advance Updated successfully",
        status_code=200,
        data=res,
    )


@router.post("/advance/request")
async def request_advance(
    SalaryAdvanceRequest: SalaryAdvanceRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    SalaryAdvanceRequest.remarks = ""
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.request_advance(SalaryAdvanceRequest)

    return RequestSalaryAdvanceResponse(
        message="Salary Advance Requested successfully",
        status_code=200,
        data=res,
    )


@router.post("/advance/respond")
async def respond_advance(
    SalaryAdvanceRespondRequest: SalaryAdvanceRespondRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.respond_salary_advance(SalaryAdvanceRespondRequest)

    return SalaryAdvanceRespondResponse(
        message="Salary Advance Responded successfully",
        status_code=200,
        data=res,
    )


@router.get("/advance/history", status_code=200)
async def get_salary_advance_history(
    employee_id: str,
    status: StatusEnum = None,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    if status and status.value == "all":
        status = None
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.get_salary_advance_history(employee_id, status)
    return {
        "message": "Salary Advance History fetched successfully",
        "status_code": 200,
        "data": res,
    }


@router.get("/advance/{salary_advance_id}", status_code=200)
async def get_salary_advance(
    salary_advance_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.get_salary_advance(salary_advance_id)
    return {
        "message": "Salary Advance fetched successfully",
        "status_code": 200,
        "data": res,
    }
