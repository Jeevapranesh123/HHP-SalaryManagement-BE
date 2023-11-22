from typing import Optional
from pydantic import BaseModel, root_validator
from enum import Enum


class SalaryAdvanceApplicationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class SalaryAdvanceBase(BaseModel):
    employee_id: str
    month: str
    amount: float


class SalaryBase(BaseModel):
    employee_id: str
    gross_salary: Optional[float] = 0.0
    pf: Optional[float] = 0.0
    esi: Optional[float] = 0.0


class MonthlyCompensationBase(BaseModel):
    employee_id: str
    loss_of_pay: Optional[float] = 0.0
    leave_cashback: Optional[float] = 0.0
    last_year_leave_cashback: Optional[float] = 0.0
    attendance_special_allowance: Optional[float] = 0.0
    other_special_allowance: Optional[float] = 0.0
    overtime: Optional[float] = 0.0


class SalaryIncentivesBase(BaseModel):
    employee_id: str
    allowance: Optional[float] = 0.0
    increment: Optional[float] = 0.0
    bonus: Optional[float] = 0.0
