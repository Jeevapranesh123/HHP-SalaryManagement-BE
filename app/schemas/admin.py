from pydantic import BaseModel, root_validator
import datetime


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