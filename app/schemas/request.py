from pydantic import (
    BaseModel,
    validator,
    root_validator,
    ValidationError,
    model_validator,
)
from fastapi import HTTPException
from app.schemas.employees import EmployeeBase, BankDetails, Address, GovtIDProofs
from app.schemas.salary import (
    SalaryBase,
    SalaryAdvanceBase,
    SalaryIncentivesBase,
    MonthlyCompensationBase,
)
from app.schemas.leave import LeaveBase, PermissionBase
from app.schemas.loan import LoanBase, LoanAdjustmentBase

from enum import Enum

import datetime
from typing import Optional
import pprint

exclude_fields_for_employee_update = ["employee_id", "email"]


# Define a phone number validator function
def validate_phone_number(cls, value, field):
    if field.name == "phone_number" and value is not None:
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be a 10-digit number")
    return value


class EmployeeCreateRequest(EmployeeBase):
    @root_validator(pre=True)
    def test(cls, values):
        basic_information = values.get("basic_information")
        if basic_information:
            for key, value in basic_information.items():
                values[key] = value.strip() if isinstance(value, str) else value

        is_marketing_staff = values.get("is_marketing_staff", None)
        is_marketing_manager = values.get("is_marketing_manager", None)

        if is_marketing_staff:
            if is_marketing_staff == "Yes":
                values["is_marketing_staff"] = True
            elif is_marketing_staff == "No":
                values["is_marketing_staff"] = False
            else:
                raise HTTPException(
                    status_code=400, detail="Is Marketing Staff must be Yes or No"
                )

        if is_marketing_staff is None:
            values["is_marketing_staff"] = False

        if is_marketing_manager:
            if is_marketing_manager == "Yes":
                values["is_marketing_manager"] = True
            elif is_marketing_manager == "No":
                values["is_marketing_manager"] = False
            else:
                raise HTTPException(
                    status_code=400, detail="Is Marketing Manager must be Yes or No"
                )

        if is_marketing_manager is None:
            values["is_marketing_manager"] = False

        if is_marketing_staff and not is_marketing_manager:
            if not values.get("marketing_manager"):
                raise HTTPException(
                    status_code=400, detail="Marketing Staff must have a manager"
                )

        for key, value in values.items():
            if isinstance(value, str):
                values[key] = value.strip()

        return values


# TODO: Keep this and EmployeeBase in sync
class EmployeeUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    branch: Optional[str] = None
    is_marketing_staff: Optional[bool] = False
    is_marketing_manager: Optional[bool] = False
    marketing_manager: Optional[str] = None
    bank_details: Optional[BankDetails] = None
    address: Optional[Address] = None
    govt_id_proofs: Optional[GovtIDProofs] = None
    # TODO: Father/Husband Phone Number (Optional) - decide on how to store this

    @root_validator(pre=True)
    def convert_basic_information(cls, values):
        basic_information = values.get("basic_information")
        if basic_information:
            for key, value in basic_information.items():
                values[key] = value
        values.pop("basic_information", None)

        is_marketing_staff = values.get("is_marketing_staff")
        is_marketing_manager = values.get("is_marketing_manager")

        if is_marketing_staff == "Yes":
            values["is_marketing_staff"] = True
        elif is_marketing_staff == "No":
            values["is_marketing_staff"] = False
        else:
            raise HTTPException(
                status_code=400, detail="Is Marketing Staff must be Yes or No"
            )

        if is_marketing_manager == "Yes":
            values["is_marketing_manager"] = True
        elif is_marketing_manager == "No":
            values["is_marketing_manager"] = False
        else:
            raise HTTPException(
                status_code=400, detail="Is Marketing Manager must be Yes or No"
            )

        if is_marketing_staff and not is_marketing_manager:
            if not values.get("marketing_manager"):
                raise HTTPException(
                    status_code=400, detail="Marketing Staff must have a manager"
                )

        if values.get("marketing_manager") == values.get("employee_id"):
            raise HTTPException(
                status_code=400,
                detail="Marketing Staff cannot be their own manager",
            )

        return values

    @validator("phone", always=True)
    def phone_validator(cls, v):
        if v is not None:
            if not v.isdigit():
                raise HTTPException(
                    status_code=400, detail="Phone number must be a number"
                )

            if len(v) != 10:
                raise HTTPException(
                    status_code=400, detail="Phone number must be 10 digits"
                )

        return v


class PostSalaryRequest(SalaryBase):
    # employee_id: str
    # gross_salary: Optional[float] = None
    # pf: Optional[float] = None
    # esi: Optional[float] = None

    @root_validator(pre=True)
    def validate(cls, values):
        for key, value in values.items():
            if value == "":
                values[key] = 0.0

            elif value is None:
                values[key] = 0.0

            elif isinstance(value, str) and key != "employee_id":
                values[key] = float(value)

        return values


class PostMonthlyCompensationRequest(MonthlyCompensationBase):
    # employee_id: str
    # loss_of_pay: Optional[float] = None
    # leave_cashback: Optional[float] = None
    # last_year_leave_cashback: Optional[float] = None
    # attendance_special_allowance: Optional[float] = None
    # other_special_allowance: Optional[float] = None
    # overtime: Optional[float] = None

    @root_validator(pre=True)
    def validate(cls, values):
        for key, value in values.items():
            if value == "":
                values[key] = 0.0

            elif value is None:
                values[key] = 0.0

            elif isinstance(value, str) and key != "employee_id":
                values[key] = float(value)

        return values


class PostSalaryIncentivesRequest(SalaryIncentivesBase):
    @root_validator(pre=True)
    def validate(cls, values):
        for key, value in values.items():
            if value == "":
                values[key] = 0.0

            elif value is None:
                values[key] = 0.0

            elif isinstance(value, str) and key != "employee_id":
                values[key] = float(value)

        return values


class LeaveCreateRequest(LeaveBase):
    no_of_days: Optional[int] = None

    @root_validator(pre=True)
    def calculate_no_of_days(cls, values):
        start_date_str = values.get("start_date")
        end_date_str = values.get("end_date")
        today = datetime.date.today()

        if start_date_str:
            start_date_obj = datetime.datetime.strptime(
                start_date_str, "%Y-%m-%d"
            ).date()

        if end_date_str:
            end_date_obj = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()

        if start_date_obj < today:
            raise HTTPException(
                status_code=400, detail="Start date cannot be in the past"
            )
        if start_date_str and end_date_str:
            if start_date_obj > end_date_obj:
                raise HTTPException(
                    status_code=400, detail="Start date must be less than end date"
                )

            if start_date_str == end_date_str:
                values["no_of_days"] = 1
            else:
                values["no_of_days"] = (
                    datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    - datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                ).days + 1
        if start_date_str and not end_date_str:
            values["end_date"] = start_date_str
            values["no_of_days"] = 1

        return values


class LeaveResponse(str, Enum):
    approved = "approved"
    rejected = "rejected"


class LeaveRespondRequest(BaseModel):
    id: str
    status: LeaveResponse
    remarks: Optional[str] = None


class PermissionCreateRequest(PermissionBase):
    @root_validator(pre=True)
    def calculate_no_of_hours(cls, values):
        start_time = values.get("start_time")
        end_time = values.get("end_time")
        date_str = values.get("date")

        start_time_str = f"{date_str} {start_time}"
        end_time_str = f"{date_str} {end_time}"

        today = datetime.datetime.today()
        now = datetime.datetime.now()

        # Ensure start_time and end_time are datetime.datetime objects
        if isinstance(start_time, str):
            try:
                start_time = datetime.datetime.strptime(
                    start_time_str, "%Y-%m-%d %H:%M"
                )
                values["start_time"] = start_time  # Update the values dictionary
            except ValueError:
                raise ValidationError(f"Invalid start_time format: {start_time}")

        if isinstance(end_time, str):
            try:
                end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                values["end_time"] = end_time  # Update the values dictionary
            except ValueError:
                raise ValidationError(f"Invalid end_time format: {end_time}")

        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_obj < today.date():
            raise HTTPException(status_code=400, detail="Date cannot be in the past")

        if date_obj == today.date() and start_time < now:
            raise HTTPException(
                status_code=400, detail="Start time cannot be in the past"
            )

        if start_time > end_time:
            raise HTTPException(
                status_code=400, detail="Start time must be less than end time"
            )
        if start_time and end_time:
            values["no_of_hours"] = (end_time - start_time).seconds / 3600

        return values


class PermissionResponse(str, Enum):
    approved = "approved"
    rejected = "rejected"


class PermissionRespondRequest(BaseModel):
    id: str
    status: PermissionResponse
    remarks: Optional[str] = None


class PaybackType(str, Enum):
    emi = "emi"
    tenure = "tenure"


class LoanCreateRequest(LoanBase):
    payback_type: PaybackType
    payback_value: int
    emi: Optional[float] = None
    tenure: Optional[int] = None

    @root_validator(pre=True)
    def calculate_emi_or_tenure(cls, values):
        amount = int(values.get("amount"))
        payback_type = values.get("payback_type")
        payback_value = int(values.get("payback_value"))

        if amount <= 0 or payback_value <= 0:
            raise HTTPException(status_code=400, detail="values must be greater than 0")

        month = values.get("month")
        month = month + "-01"
        values["month"] = datetime.datetime.strptime(month, "%Y-%m-%d").date()
        if payback_type == "emi":
            if not payback_value:
                raise ValueError("EMI must be provided for EMI payback type")

            if payback_value > amount:
                raise HTTPException(
                    status_code=400, detail="EMI must be less than loan amount"
                )
            values["tenure"] = (
                amount / payback_value
                if amount % payback_value == 0
                else amount // payback_value + 1
            )
            values["emi"] = payback_value

        elif payback_type == "tenure":
            if not payback_value:
                raise ValueError("Tenure must be provided for Tenure payback type")
            values["emi"] = amount / payback_value
            values["tenure"] = payback_value

        else:
            raise ValueError("Invalid payback type")

        return values


class LoanAdjustmentRequest(BaseModel):
    loan_id: str
    month: datetime.date = datetime.date.today().replace(day=1)
    new_amount: Optional[float] = None
    skip_months: Optional[int] = None
    remarks: Optional[str] = None


class LoanResponse(str, Enum):
    approved = "approved"
    rejected = "rejected"


class LoanRespondRequest(BaseModel):
    loan_id: str
    status: LoanResponse
    remarks: Optional[str] = None
    data_change: Optional[dict] = None

    @root_validator(pre=True)
    def validate_data_change(cls, values):
        amount = values.get("amount")
        emi = values.get("emi")

        values["data_change"] = {}
        if amount:
            amount = int(amount)
            if amount <= 0:
                raise HTTPException(
                    status_code=400, detail="Amount must be greater than 0"
                )
            values["data_change"]["amount"] = amount

        if emi:
            emi = float(emi)
            if emi <= 0:
                raise HTTPException(
                    status_code=400, detail="EMI must be greater than 0"
                )

            values["data_change"]["emi"] = emi

        if not values["data_change"]:
            values.pop("data_change")

        return values


class SalaryAdvanceRequest(SalaryAdvanceBase):
    @root_validator(pre=True)
    def convert_month_to_datetime(cls, values):
        month = values.get("month")
        month = month + "-01"
        if isinstance(month, str):
            try:
                month = datetime.datetime.strptime(month, "%Y-%m-%d").date()
                values["month"] = month  # Update the values dictionary
            except ValueError:
                raise ValidationError(f"Invalid month format: {month}")

        return values


class SalaryAdvanceResponse(str, Enum):
    approved = "approved"
    rejected = "rejected"


class SalaryAdvanceRespondRequest(BaseModel):
    id: str
    status: SalaryAdvanceResponse
    remarks: Optional[str] = None


class LoanAdjustmentRequest(LoanAdjustmentBase):
    pass
