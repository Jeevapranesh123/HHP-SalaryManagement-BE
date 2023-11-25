from app.database import AsyncIOMotorClient

from app.schemas.request import LoanCreateRequest, LoanRespondRequest
from app.schemas.loan import LoanBase

from app.api.crud import loan as loan_crud


class LoanController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.employee_id = payload["employee_id"]
        self.employee_role = payload["primary_role"]
        self.mongo_client = mongo_client

    async def request_loan(
        self,
        LoanCreateRequest: LoanCreateRequest,
    ):
        print(LoanCreateRequest.model_dump())
        loan_in_create = LoanBase(**LoanCreateRequest.model_dump())
        return await loan_crud.request_loan(
            loan_in_create, self.mongo_client, "request", self.employee_id
        )

    async def respond_loan(
        self,
        LoanRespondRequest: LoanRespondRequest,
    ):
        print(LoanRespondRequest.model_dump())
        return await loan_crud.respond_loan(LoanRespondRequest, self.mongo_client)
