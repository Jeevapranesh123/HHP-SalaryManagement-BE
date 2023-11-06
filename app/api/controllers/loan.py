from app.database import AsyncIOMotorClient

from app.schemas.request import LoanCreateRequest, LoanRespondRequest
from app.schemas.loan import LoanBase

from app.api.crud import loan as loan_crud


async def request_loan(
    LoanCreateRequest: LoanCreateRequest,
    mongo_client: AsyncIOMotorClient,
):
    print(LoanCreateRequest.model_dump())
    loan_in_create = LoanBase(**LoanCreateRequest.model_dump())
    return await loan_crud.request_loan(loan_in_create, mongo_client)


async def respond_loan(
    LoanRespondRequest: LoanRespondRequest,
    mongo_client: AsyncIOMotorClient,
):
    print(LoanRespondRequest.model_dump())
    return await loan_crud.respond_loan(LoanRespondRequest, mongo_client)
