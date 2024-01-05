from pydantic import BaseModel, root_validator, Field
import datetime
from typing import List, Dict
from enum import Enum
import uuid


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


class BankSalaryBatch(BaseModel):
    batch_name: str
    employee_ids: List[str]


class BankSalaryBatchInDB(BankSalaryBatch):
    branch: str
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))
    created_at: datetime.datetime = datetime.datetime.now()
    created_by: str = "MD"
    updated_at: datetime.datetime = None
    updated_by: str = None


class BankSalaryBatchCreateRequest(BankSalaryBatch):
    pass


class BankSalaryBatchResponse(BaseModel):
    batch_id: str
    batch_name: str
    branch: str
    employee_ids: List[str]


class BankSalaryBatchCreateResponse(BaseModel):
    message: str
    status: bool
    data: BankSalaryBatchResponse


class BankSalaryBatchUpdateRequest(BankSalaryBatch):
    batch_id: str
