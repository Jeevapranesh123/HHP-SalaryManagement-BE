from app.database import AsyncIOMotorClient

from app.schemas.request import (
    SalaryCreateRequest,
    SalaryAdvanceRequest,
    SalaryAdvanceRespondRequest,
)
from app.schemas.salary import SalaryBase


from app.api.crud import salary as salary_crud


async def get_all_salaries(mongo_client: AsyncIOMotorClient):
    return await salary_crud.get_all_salaries(mongo_client)


async def create_salary(
    SalaryCreateRequest: SalaryCreateRequest, mongo_client: AsyncIOMotorClient
):
    salary_in_create = SalaryBase(**SalaryCreateRequest.model_dump())
    return await salary_crud.create_salary(salary_in_create, mongo_client)


async def request_advance(
    SalaryAdvanceRequest: SalaryAdvanceRequest, mongo_client: AsyncIOMotorClient
):
    return await salary_crud.request_advance(SalaryAdvanceRequest, mongo_client)


async def respond_salary_advance(
    SalaryAdvanceRespondRequest: SalaryAdvanceRespondRequest,
    mongo_client: AsyncIOMotorClient,
):
    return await salary_crud.respond_salary_advance(
        SalaryAdvanceRespondRequest, mongo_client
    )
