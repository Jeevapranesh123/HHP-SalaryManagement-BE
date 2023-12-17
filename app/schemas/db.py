from app.schemas.employees import EmployeeBase
from app.schemas.salary import (
    SalaryBase,
    SalaryAdvanceBase,
    SalaryAdvanceApplicationStatus,
    MonthlyCompensationBase,
    SalaryIncentivesBase,
)
from app.schemas.leave import LeaveBase, PermissionBase, LeaveApplicationStatus
from app.schemas.loan import LoanBase, LoanApplicationStatus
import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, Field


def first_day_of_current_month():
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, 1, 0, 0, 0)


class EmployeeInDB(EmployeeBase):
    pass


class SalaryInDB(SalaryBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))

    month: datetime.datetime = first_day_of_current_month()
    created_at: datetime.datetime = datetime.datetime.now()
    created_by: str = "admin"
    updated_at: datetime.datetime = None
    updated_by: str = None


class MonthlyCompensationInDB(MonthlyCompensationBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))

    month: datetime.datetime = first_day_of_current_month()
    created_at: datetime.datetime = datetime.datetime.now()
    created_by: str = "admin"
    updated_at: datetime.datetime = None
    updated_by: str = None


class SalaryIncentivesInDB(SalaryIncentivesBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))

    month: datetime.datetime = first_day_of_current_month()
    created_at: datetime.datetime = datetime.datetime.now()
    created_by: str = "admin"
    updated_at: datetime.datetime = None
    updated_by: str = None


class LeaveInDB(LeaveBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))

    type: str = "leave"
    leave_type: str = "casual"
    start_date: datetime.datetime
    end_date: datetime.datetime
    # FIXME: Store the month and year in which the leave was taken
    month: datetime.datetime
    status: Optional[LeaveApplicationStatus] = "pending"
    remarks: Optional[str] = ""
    requested_at: datetime.datetime = datetime.datetime.now()
    requested_by: str
    approved_or_rejected_by: str = "admin"
    approved_or_rejected_at: datetime.datetime = None


class PermissionInDB(PermissionBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))

    type: str = "permission"
    leave_type: str = "permission"
    start_time: datetime.datetime
    end_time: datetime.datetime
    date: datetime.datetime
    month: datetime.datetime
    status: Optional[LeaveApplicationStatus] = "pending"
    remarks: Optional[str] = ""
    requested_at: datetime.datetime = datetime.datetime.now()
    requested_by: str
    approved_or_rejected_by: str = "admin"
    approved_or_rejected_at: datetime.datetime = None


class LoanInDB(LoanBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))

    type: str = "loan"
    month: datetime.datetime
    status: Optional[LoanApplicationStatus] = "pending"
    remarks: Optional[str] = ""
    requested_at: datetime.datetime = datetime.datetime.now()
    requested_by: str
    approved_or_rejected_by: str = "admin"
    approved_or_rejected_at: datetime.datetime = None
    is_completed: bool = False
    repayment_schedule: Optional[list] = None


class SalaryAdvanceInDB(SalaryAdvanceBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))

    month: datetime.datetime
    type: str = "salary_advance"
    status: Optional[SalaryAdvanceApplicationStatus] = "pending"
    remarks: Optional[str] = ""
    requested_at: datetime.datetime = datetime.datetime.now()
    requested_by: str
    approved_or_rejected_by: str = None
    approved_or_rejected_at: datetime.datetime = None
