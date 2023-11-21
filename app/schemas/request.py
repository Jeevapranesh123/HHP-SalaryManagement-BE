from pydantic import BaseModel, validator
from fastapi import HTTPException
from app.schemas.employees import EmployeeBase, BankDetails, Address, GovtIDProofs
from app.schemas.salary import SalaryBase, SalaryAdvanceBase
from app.schemas.leave import LeaveBase, PermissionBase
from app.schemas.loan import LoanBase

from enum import Enum

from pydantic import Field, create_model


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


# EmployeeUpdateRequest = create_model(
#     "EmployeeUpdateRequest",
#     **{
#         name: (Optional[EmployeeBase.__annotations__[name]], None)
#         for name, field in EmployeeBase.__annotations__.items()
#         if name not in exclude_fields_for_employee_update
#     }
# )


class EmployeeUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    bank_details: Optional[BankDetails] = None
    address: Optional[Address] = None
    govt_id_proofs: Optional[GovtIDProofs] = None
    # TODO: Father/Husband Phone Number (Optional) - decide on how to store this

    @validator("phone")
    def phone_validator(cls, v):
        if len(v) != 10:
            raise HTTPException(
                status_code=400, detail="Phone number must be 10 digits"
            )
        return v


class SalaryCreateRequest(SalaryBase):
    pass


class LeaveCreateRequest(LeaveBase):
    status: Optional[str] = Field(None, exclude=True)

    class Config:
        exclude = {"status"}


class LeaveResponse(str, Enum):
    approved = "approved"
    rejected = "rejected"


class LeaveRespondRequest(BaseModel):
    leave_id: str
    status: LeaveResponse
    remarks: Optional[str] = None


class PermissionCreateRequest(PermissionBase):
    status: Optional[str] = Field(None, exclude=True)

    class Config:
        exclude = {"status"}


class PermissionResponse(str, Enum):
    approved = "approved"
    rejected = "rejected"


class PermissionRespondRequest(BaseModel):
    permission_id: str
    status: PermissionResponse
    remarks: Optional[str] = None


class LoanCreateRequest(LoanBase):
    status: Optional[str] = Field(None, exclude=True)

    class Config:
        exclude = {"status"}


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
