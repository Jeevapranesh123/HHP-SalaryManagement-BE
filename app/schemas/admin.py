from pydantic import BaseModel, root_validator
import datetime
from typing import List, Dict
from enum import Enum


class Rules(BaseModel):
    total_leave: str
    medical_leave: str
    permission: str
    loan: str
    increment: str


class RulesInDB(Rules):
    id: str = "rules"
    created_at: datetime.datetime
    created_by: str = "MD"
    updated_at: datetime.datetime
    updated_by: str = "MD"


class Guidelines(BaseModel):
    guidelines: List[Dict]


class ReportType(str, Enum):
    salary = "salary"
    increment = "increment"
    bonus = "bonus"
    allowance = "allowance"
    attendance_special_allowance = "attendance_special_allowance"
    other_special_allowance = "other_special_allowance"
    leave = "leave"
    all = "all"
