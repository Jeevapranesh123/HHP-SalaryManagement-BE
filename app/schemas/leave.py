from pydantic import BaseModel, root_validator
from typing import List, Optional
import datetime
from enum import Enum
from pydantic import BaseModel, root_validator, ValidationError


class LeaveType(str, Enum):
    casual = "casual"
    medical = "medical"


class LeaveMonth(str, Enum):
    january = "january"
    february = "february"
    march = "march"
    april = "april"
    may = "may"
    june = "june"
    july = "july"
    august = "august"
    september = "september"
    october = "october"
    november = "november"
    december = "december"


class LeaveApplicationStatus(str, Enum):
    approved = "approved"
    pending = "pending"
    rejected = "rejected"


class LeaveBase(BaseModel):
    employee_id: str
    type: LeaveType
    start_date: datetime.date
    end_date: Optional[datetime.date] = None
    no_of_days: Optional[int] = None
    reason: str
    remarks: Optional[str] = ""


class PermissionBase(BaseModel):
    employee_id: str
    type: str = "permission"
    date: datetime.date
    start_time: datetime.datetime
    end_time: datetime.datetime
    no_of_hours: float
    reason: str
