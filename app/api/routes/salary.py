from fastapi import APIRouter, Depends, Response, Request


# import DB Utils
from app.database import get_mongo, AsyncIOMotorClient

from app.api.controllers import salary as salary_controller

from app.schemas.request import (
    SalaryCreateRequest,
    SalaryAdvanceRequest,
    SalaryAdvanceRespondRequest,
)
from app.schemas.response import SalaryCreateResponse, SalaryResponse


router = APIRouter()


@router.get("/", status_code=200)
async def get_all_salaries(mongo_client: AsyncIOMotorClient = Depends(get_mongo)):
    return await salary_controller.get_all_salaries(mongo_client)


@router.post("/", status_code=201, response_model=SalaryCreateResponse)
async def create_salary(
    SalaryCreateRequest: SalaryCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await salary_controller.create_salary(SalaryCreateRequest, mongo_client)

    return SalaryCreateResponse(
        message="Salary created successfully",
        status_code=201,
        data=SalaryResponse(
            employee_id=res.employee_id,
            basic=res.basic,
            net_salary=res.net_salary,
        ),
    )


@router.post("/request_advance")
async def request_advance(
    SalaryAdvanceRequest: SalaryAdvanceRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await salary_controller.request_advance(SalaryAdvanceRequest, mongo_client)


@router.post("/respond_advance")
async def respond_advance(
    SalaryAdvanceRespondRequest: SalaryAdvanceRespondRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await salary_controller.respond_salary_advance(
        SalaryAdvanceRespondRequest, mongo_client
    )
