from pydantic import BaseModel, root_validator
from typing import List, Optional
import datetime
from enum import Enum


class LoanApplicationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class LoanBase(BaseModel):
    employee_id: str
    amount: float
    month: str
    emi: Optional[float] = None
    tenure: Optional[int] = None

    @root_validator(pre=True)
    def calculate_emi(cls, values):
        amount = values.get("amount")
        tenure = values.get("tenure")
        emi = values.get("emi")
        if amount and tenure:
            values["emi"] = amount / tenure
            return values

        if amount and emi:
            values["tenure"] = amount / emi
            return values
