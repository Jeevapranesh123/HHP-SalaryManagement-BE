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
from app.api.crud import auth as auth_crud


from app.api.lib.Notification import Notification
from app.schemas.notification import (
    NotificationBase,
    SendNotification,
    NotificationMeta,
)


class LoanController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.employee_id = payload["employee_id"]
        self.employee_role = payload["primary_role"]
        self.employee_name = payload["employee_name"]
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

        emp = await employee_crud.get_employee(
            loan_in_create.employee_id, self.mongo_client
        )
        if not emp:
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(loan_in_create["employee_id"]),
            )
        res = await loan_crud.request_loan(
            loan_in_create, self.mongo_client, "post", self.employee_id
        )
        res["loan_id"] = res["id"]
        await loan_crud.build_repayment_schedule(res, self.mongo_client)

        user = await auth_crud.get_user_with_employee_id(
            loan_in_create.employee_id, self.mongo_client
        )

        branch = emp["branch"]

        notification = Notification(self.employee_id, "post_loan", self.mongo_client)

        notifiers = [res["employee_id"]]

        emp_notification = NotificationBase(
            title="Loan Approved",
            description="Loan has been approved for you",
            payload={"url": "/loan/history"},
            ui_action="action",
            source="loan",
            type="loan",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        send = SendNotification(notifier=[emp_notification])

        await notification.send_notification(send)

        return res

    async def request_loan(
        self,
        LoanCreateRequest: LoanCreateRequest,
    ):
        loan_in_create = LoanBase(**LoanCreateRequest.model_dump())
        emp = await employee_crud.get_employee(
            loan_in_create.employee_id, self.mongo_client
        )
        if not emp:
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

        user = await auth_crud.get_user_with_employee_id(
            loan_in_create.employee_id, self.mongo_client
        )

        branch = emp["branch"]

        notification = Notification(self.employee_id, "request_loan", self.mongo_client)

        notifiers = [res["employee_id"], "MD"]

        emp_notification = NotificationBase(
            title="Loan Requested",
            description="{} has requested a loan for you".format(self.employee_name),
            payload={"url": "/loan/history"},
            ui_action="action",
            type="loan",
            source="request_loan",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Loan Requested",
            description="{} has requested a loan".format(self.employee_name),
            payload={
                "url": "/employees/{}/loan/respond?id={}".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="loan",
            source="request_loan",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = []

        if self.employee_role == "MD":
            notifier = [emp_notification]

        elif self.employee_role == "employee":
            notifier = [md_notification]

        send = SendNotification(notifier=notifier)

        await notification.send_notification(send)

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

        user = await auth_crud.get_user_with_employee_id(
            res["employee_id"], self.mongo_client
        )

        branch = user["info"]["branch"]

        notification = Notification(self.employee_id, "respond_loan", self.mongo_client)

        notifiers = [res["employee_id"]]

        emp_notification = NotificationBase(
            title="Loan {}".format(res["status"].capitalize()),
            description="Loan has been {} for you".format(res["status"]),
            payload={"url": "/loan/history"},
            ui_action="action",
            source="loan",
            type="loan",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        send = SendNotification(notifier=[emp_notification])

        await notification.send_notification(send)

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
