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


def first_day_of_current_month():
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, 1, 0, 0, 0)


class EmployeeInDB(EmployeeBase):
    pass


class SalaryInDB(SalaryBase):
    id: str
    created_at: datetime.datetime = datetime.datetime.now()
    created_by: str = "admin"
    updated_at: datetime.datetime = None
    updated_by: str = None


class MonthlyCompensationInDB(MonthlyCompensationBase):
    id: str
    month: datetime.datetime = first_day_of_current_month()
    created_at: datetime.datetime = datetime.datetime.now()
    created_by: str = "admin"
    updated_at: datetime.datetime = None
    updated_by: str = None


class SalaryIncentivesInDB(SalaryIncentivesBase):
    id: str
    month: datetime.datetime = first_day_of_current_month()
    created_at: datetime.datetime = datetime.datetime.now()
    created_by: str = "admin"
    updated_at: datetime.datetime = None
    updated_by: str = None


class LeaveInDB(LeaveBase):
    id: str
    type: str = "leave"
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
    id: str
    type: str = "permission"
    date: datetime.datetime
    start_time: datetime.datetime
    end_time: datetime.datetime
    status: Optional[LeaveApplicationStatus] = "pending"
    remarks: Optional[str] = ""
    requested_at: datetime.datetime = datetime.datetime.now()
    requested_by: str
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
