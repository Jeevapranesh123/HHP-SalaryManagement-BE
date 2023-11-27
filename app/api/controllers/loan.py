from app.database import AsyncIOMotorClient

from app.schemas.request import LoanCreateRequest, LoanRespondRequest
from app.schemas.loan import LoanBase
from fastapi import HTTPException
from app.api.crud import loan as loan_crud
from app.api.crud import employees as employee_crud
from app.api.utils.auth import role_required


class LoanController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.employee_id = payload["employee_id"]
        self.employee_role = payload["primary_role"]
        self.mongo_client = mongo_client

    async def get_loan_history(self, employee_id, status):
        if not self.employee_role in ["HR", "MD"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return await loan_crud.get_loan_history(employee_id, status, self.mongo_client)

    # @role_required(["MD"])
    async def post_loan(
        self,
        LoanCreateRequest: LoanCreateRequest,
    ):
        loan_in_create = LoanBase(**LoanCreateRequest.model_dump())

        if not await employee_crud.get_employee(
            loan_in_create.employee_id, self.mongo_client
        ):
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(loan_in_create["employee_id"]),
            )
        res = await loan_crud.request_loan(
            loan_in_create, self.mongo_client, "post", self.employee_id
        )
        res["loan_id"] = res["id"]
        await loan_crud.build_repayment_schedule(res, self.mongo_client)
        return res

    async def request_loan(
        self,
        LoanCreateRequest: LoanCreateRequest,
    ):
        loan_in_create = LoanBase(**LoanCreateRequest.model_dump())
        if not await employee_crud.get_employee(
            loan_in_create.employee_id, self.mongo_client
        ):
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(loan_in_create.employee_id),
            )

        if (
            not self.employee_role in ["HR", "MD"]
            and loan_in_create.employee_id != self.employee_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        res = await loan_crud.request_loan(
            loan_in_create, self.mongo_client, "request", self.employee_id
        )
        res["loan_id"] = res["id"]

        return res

    async def get_loan(self, loan_id):
        loan = await loan_crud.get_loan(loan_id, self.mongo_client)
        if not loan:
            raise HTTPException(status_code=404, detail="Loan record not found")
        if not self.employee_role in ["MD"] and loan["employee_id"] != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        loan["loan_id"] = loan["id"]
        return loan

    async def respond_loan(
        self,
        LoanRespondRequest: LoanRespondRequest,
    ):
        loan_respond_request = LoanRespondRequest.model_dump()
        if not await self.get_loan(loan_respond_request["loan_id"]):
            raise HTTPException(status_code=404, detail="Loan record not found")

        res = await loan_crud.respond_loan(
            loan_respond_request, self.mongo_client, self.employee_id
        )
        repayment_schedule = await loan_crud.build_repayment_schedule(
            res, self.mongo_client
        )
        res["loan_id"] = res["id"]
        res["repayment_schedule"] = repayment_schedule
        return res
