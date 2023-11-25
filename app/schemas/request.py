from pydantic import BaseModel, validator, root_validator
from fastapi import HTTPException
from app.schemas.employees import EmployeeBase, BankDetails, Address, GovtIDProofs
from app.schemas.salary import SalaryBase, SalaryAdvanceBase
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


class PostSalaryIncentivesRequest(BaseModel):
    employee_id: str
    allowance: Optional[float] = None
    increment: Optional[float] = None
    bonus: Optional[float] = None


class LeaveCreateRequest(LeaveBase):
    no_of_days: Optional[int] = None

    @root_validator(pre=True)
    def calculate_no_of_days(cls, values):
        start_date_str = values.get("start_date")
        end_date_str = values.get("end_date")
        if start_date_str and end_date_str:
            print(1)
            if start_date_str == end_date_str:
                print(2)
                values["no_of_days"] = 1
            else:
                values["no_of_days"] = (
                    datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    - datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                ).days
        if start_date_str and not end_date_str:
            print(3)
            values["end_date"] = start_date_str
            values["no_of_days"] = 1

        print(values)
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
        # Ensure start_time and end_time are datetime.datetime objects
        if isinstance(start_time, str):
            try:
                start_time = datetime.datetime.fromisoformat(start_time)
                values["start_time"] = start_time  # Update the values dictionary
            except ValueError:
                raise ValidationError(f"Invalid start_time format: {start_time}")

        if isinstance(end_time, str):
            try:
                end_time = datetime.datetime.fromisoformat(end_time)
                values["end_time"] = end_time  # Update the values dictionary
            except ValueError:
                raise ValidationError(f"Invalid end_time format: {end_time}")

        if start_time > end_time:
            raise ValueError("start_time must be less than end_time")
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


class PaybackType(str, Enum):
    emi = "emi"
    tenure = "tenure"


class LoanCreateRequest(LoanBase):
    payback_type: PaybackType

    @root_validator(pre=True)
    def calculate_emi_or_tenure(cls, values):
        amount = values.get("amount")
        tenure = values.get("tenure")
        emi = values.get("emi")
        payback_type = values.get("payback_type")

        if payback_type == "emi":
            if not emi:
                raise ValueError("EMI must be provided for EMI payback type")
            values["tenure"] = amount % emi if amount % emi == 0 else amount // emi + 1

        elif payback_type == "tenure":
            if not tenure:
                raise ValueError("Tenure must be provided for tenure payback type")
            values["emi"] = amount / tenure

        else:
            raise ValueError("Invalid payback type")

        return values


class LoanResponse(str, Enum):
    approved = "approved"
    rejected = "rejected"


class LoanRespondRequest(BaseModel):
    loan_id: str
    status: LoanResponse
    remarks: Optional[str] = None


class SalaryAdvanceRequest(SalaryAdvanceBase):
    pass


class SalaryAdvanceResponse(str, Enum):
    approved = "approved"
    rejected = "rejected"


class SalaryAdvanceRespondRequest(BaseModel):
    salary_advance_id: str
    status: SalaryAdvanceResponse
    remarks: Optional[str] = None
    data_change: Optional[dict] = None
