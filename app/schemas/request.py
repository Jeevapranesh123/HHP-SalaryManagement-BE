from pydantic import BaseModel

from app.schemas.employees import EmployeeBase
from app.schemas.salary import SalaryBase, SalaryAdvanceBase
from app.schemas.leave import LeaveBase, PermissionBase
from app.schemas.loan import LoanBase

from enum import Enum

from pydantic import Field


from typing import Optional


class EmployeeCreateRequest(EmployeeBase):
    # employees: Employee
    pass


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
