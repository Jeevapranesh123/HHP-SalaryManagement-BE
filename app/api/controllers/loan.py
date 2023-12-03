from app.database import AsyncIOMotorClient

from app.schemas.request import (
    LoanCreateRequest,
    LoanRespondRequest,
    LoanAdjustmentRequest,
)
from app.schemas.loan import LoanBase
from fastapi import HTTPException
from app.api.crud import loan as loan_crud
from app.api.crud import employees as employee_crud
from app.api.utils.auth import role_required

import math
import datetime


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
        if res["status"] == "approved":
            repayment_schedule = await loan_crud.build_repayment_schedule(
                res, self.mongo_client
            )
        res["loan_id"] = res["id"]
        return res

    # async def adjust_loan(self, LoanRespondRequest: LoanRespondRequest):

    async def get_repayment_schedule(self, loan_id):
        loan = await loan_crud.get_loan(loan_id, self.mongo_client)
        if not loan:
            raise HTTPException(status_code=404, detail="Loan record not found")
        if not self.employee_role in ["MD"] and loan["employee_id"] != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        repayment_schedule = await loan_crud.get_repayment_schedule(
            loan_id, self.mongo_client
        )
        return repayment_schedule

    async def get_repayment_emi(self, repayment_id):
        repayment_emi = await loan_crud.get_repayment_emi(
            repayment_id, self.mongo_client
        )

        if not repayment_emi:
            raise HTTPException(status_code=404, detail="Repayment record not found")

        if (
            not self.employee_role in ["MD"]
            and repayment_emi["employee_id"] != self.employee_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        outstanding_amount = await loan_crud.get_outstanding_amount_for_loan(
            repayment_emi["loan_id"], repayment_emi["month"], self.mongo_client
        )

        repayment_emi["loan_outstanding"] = outstanding_amount["repayment_outstanding"]
        repayment_emi["tenure_remaining"] = outstanding_amount["tenure_remaining"]

        return repayment_emi

    async def get_loan_adjust_meta(self):
        return {
            "data": {
                "employee_id": {
                    "type": "string",
                    "required": True,
                    "editable": False,
                },
                "loan_outstanding": {
                    "type": "number",
                    "required": True,
                    "editable": False,
                },
                "loan_id": {
                    "type": "string",
                    "required": True,
                    "editable": False,
                },
                "repayment_id": {
                    "type": "string",
                    "required": True,
                    "editable": False,
                },
                "old_emi": {
                    "type": "number",
                    "required": True,
                },
                "new_emi": {
                    "type": "number",
                    "required": True,
                },
                # "adjustment_month": {
                #     "type": "month",
                #     "required": False,
                # },
                "remarks": {
                    "type": "textarea",
                    "required": True,
                },
            },
            "actions": [
                {
                    "label": "Adjust",
                    "type": "button",
                    "variant": "default",
                    "action": {"url": "/loan/adjust", "method": "POST"},
                }
            ],
        }

    async def adjust_loan(self, LoanAdjustmentRequest):
        loan_adjustment_request = LoanAdjustmentRequest.model_dump()

        loan = await self.get_loan(loan_adjustment_request["loan_id"])

        if not loan:
            raise HTTPException(status_code=404, detail="Loan record not found")

        return True

        # if loan_adjustment_request["old_emi"] == loan_adjustment_request["new_emi"]:
        #     raise HTTPException(status_code=400, detail="Old and new EMI cannot be same")

        # adjustment_month = datetime.datetime.combine(
        #     loan_adjustment_request["adjustment_month"], datetime.datetime.min.time()
        # )
        # print(adjustment_month)
        # emi_diff = math.ceil(loan_adjustment_request["new_emi"] - loan_adjustment_request["old_emi"])

        # if emi_diff == 0:
        #     raise HTTPException(status_code=400, detail="Old and new EMI cannot be same")

        # remaining_months = await loan_crud.get_outstanding_months_by_range(
        #     loan_adjustment_request["loan_id"],
        #     self.mongo_client,
        #     start_month=adjustment_month,
        # )

        # current_last_month = remaining_months[-1]

        # if current_last_month["amount"] +
