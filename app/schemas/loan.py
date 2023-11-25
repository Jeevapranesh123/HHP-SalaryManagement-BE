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
    month: datetime.date = datetime.date.today().replace(day=1)
    emi: Optional[float] = None
    tenure: Optional[int] = None
