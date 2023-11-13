from typing import Optional
from pydantic import BaseModel, root_validator
from enum import Enum


class SalaryBase(BaseModel):
    employee_id: str
    gross: float
    pf: float
    esi: float

    # @root_validator
    # def validate_net_salary(cls, values):
    #     net = values["basic"] + values["hra"] + values["conveyance"] - values["pf"]*12 - values["esi"]*12


class SalaryAdvanceApplicationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class SalaryAdvanceBase(BaseModel):
    employee_id: str
    month: str
    amount: float


class Temp(BaseModel):
    employee_id: str
    loss_of_pay: float
    leave_cashback: float
    last_year_leave_cashback: float
    attendance_special_allowance: float
