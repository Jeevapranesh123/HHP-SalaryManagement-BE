from app.schemas.employees import EmployeeBase
from app.schemas.salary import (
    SalaryBase,
    SalaryAdvanceBase,
    SalaryAdvanceApplicationStatus,
)
from app.schemas.leave import LeaveBase, PermissionBase, LeaveApplicationStatus
from app.schemas.loan import LoanBase, LoanApplicationStatus
import datetime
from typing import Optional


class EmployeeInDB(EmployeeBase):
    pass


class SalaryInDB(SalaryBase):
    id: str
    created_at: datetime.datetime = datetime.datetime.now()
    created_by: str = "admin"
    updated_at: datetime.datetime = None
    updated_by: str = None


class LeaveInDB(LeaveBase):
    id: str
    type: str = "leave"
    start_date: datetime.datetime
    end_date: datetime.datetime
    status: Optional[LeaveApplicationStatus] = "pending"
    requested_at: datetime.datetime = datetime.datetime.now()
    approved_or_rejected_by: str = "admin"
    approved_or_rejected_at: datetime.datetime = None


class PermissionInDB(PermissionBase):
    id: str
    type: str = "permission"
    date: datetime.datetime
    start_time: datetime.datetime
    end_time: datetime.datetime
    status: Optional[LeaveApplicationStatus] = "pending"
    requested_at: datetime.datetime = datetime.datetime.now()
    approved_or_rejected_by: str = "admin"
    approved_or_rejected_at: datetime.datetime = None


class LoanInDB(LoanBase):
    id: str
    type: str = "loan"
    status: Optional[LoanApplicationStatus] = "pending"
    requested_at: datetime.datetime = datetime.datetime.now()
    approved_or_rejected_by: str = "admin"
    approved_or_rejected_at: datetime.datetime = None


class SalaryAdvanceInDB(SalaryAdvanceBase):
    id: str
    type: str = "salary_advance"
    status: Optional[SalaryAdvanceApplicationStatus] = "pending"
    requested_at: datetime.datetime = datetime.datetime.now()
    approved_or_rejected_by: str = "admin"
    approved_or_rejected_at: datetime.datetime = None
