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
from app.schemas.salary import (
    MonthlyCompensationBase,
    SalaryIncentivesBase,
)  # FIXME: Create a Request and Response Schema for Temp Salary
from app.schemas.response import (
    PostSalaryResponse,
    PostMonthlyCompensationResponse,
    PostSalaryIncentivesResponse,
    PostSalaryAdvanceResponse,
    RequestSalaryAdvanceResponse,
    SalaryAdvanceRespondResponse,
)
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
    print(res)
    return SalaryAdvanceRespondResponse(
        message="Salary Advance Responded successfully",
        status_code=200,
        data=res,
    )


@router.get("/advance/history", status_code=200)
async def get_salary_advance_history(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    sal_obj = SalaryController(payload, mongo_client)
    res = await sal_obj.get_salary_advance_history(employee_id)
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
