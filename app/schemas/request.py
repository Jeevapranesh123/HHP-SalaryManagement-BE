from pydantic import BaseModel, validator, root_validator
from fastapi import HTTPException
from app.schemas.employees import EmployeeBase, BankDetails, Address, GovtIDProofs
from app.schemas.salary import SalaryBase, SalaryAdvanceBase, SalaryIncentivesBase
from app.schemas.leave import LeaveBase, PermissionBase
from app.schemas.loan import LoanBase

from enum import Enum

from pydantic import Field, create_model, ValidationError
import datetime
from typing import Optional

exclude_fields_for_employee_update = ["employee_id", "email"]


# Define a phone number validator function
def validate_phone_number(cls, value, field):
    if field.name == "phone_number" and value is not None:
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be a 10-digit number")
    return value


class EmployeeCreateRequest(EmployeeBase):
    # employees: Employee
    pass


class EmployeeUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    bank_details: Optional[BankDetails] = None
    address: Optional[Address] = None
    govt_id_proofs: Optional[GovtIDProofs] = None
    # TODO: Father/Husband Phone Number (Optional) - decide on how to store this

    @validator("phone", always=True)
    def phone_validator(cls, v):
        if v is not None and len(v) != 10:
            raise HTTPException(
                status_code=400, detail="Phone number must be 10 digits"
            )
        return v


# class SalaryCreateRequest(SalaryBase):
#     pass


class PostSalaryRequest(BaseModel):
    employee_id: str
    gross_salary: Optional[float] = None
    pf: Optional[float] = None
    esi: Optional[float] = None


class PostMonthlyCompensationRequest(BaseModel):
    employee_id: str
    loss_of_pay: Optional[float] = None
    leave_cashback: Optional[float] = None
    last_year_leave_cashback: Optional[float] = None
    attendance_special_allowance: Optional[float] = None
    other_special_allowance: Optional[float] = None
    overtime: Optional[float] = None


class PostSalaryIncentivesRequest(SalaryIncentivesBase):
    pass


class LeaveCreateRequest(LeaveBase):
    no_of_days: Optional[int] = None

    @root_validator(pre=True)
    def calculate_no_of_days(cls, values):
        start_date_str = values.get("start_date")
        end_date_str = values.get("end_date")
        if start_date_str and end_date_str:
            start_date_obj = datetime.datetime.strptime(
                start_date_str, "%Y-%m-%d"
            ).date()
            end_date_obj = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
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
                ).days
        if start_date_str and not end_date_str:
            values["end_date"] = start_date_str
            values["no_of_days"] = 1

        return values


class LeaveResponse(str, Enum):
    approved = "approved"
    rejected = "rejected"


class LeaveRespondRequest(BaseModel):
    leave_id: str
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
    permission_id: str
    status: PermissionResponse
    remarks: Optional[str] = None

    @root_validator(pre=True)
    def check(cls, values):
        print(type(values))
        values["permission_id"] = values.get("id", None)


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

        month = values.get("month")
        month = month + "-01"
        values["month"] = datetime.datetime.strptime(month, "%Y-%m-%d").date()
        if payback_type == "emi":
            if not payback_value:
                raise ValueError("EMI must be provided for EMI payback type")
            print(payback_value)
            print(amount)
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
    salary_advance_id: str
    status: SalaryAdvanceResponse
    remarks: Optional[str] = None
    data_change: Optional[dict] = None

    @root_validator(pre=True)
    def check(cls, values):
        print(values)
