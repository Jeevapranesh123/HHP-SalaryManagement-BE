from typing import Optional
from pydantic import BaseModel, root_validator
from enum import Enum


class SalaryBase(BaseModel):
    employee_id: str
    basic: float
    hra: Optional[float] = None
    conveyance: Optional[float] = None
    pf: float
    esi: float
    net_salary: float

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
