from pydantic import BaseModel
from typing import Optional

import uuid


class AttendanceBase(BaseModel):
    employee_id: str
    date: str
    status: str


class AttendanceInDB(AttendanceBase):
    id: str = str(uuid.uuid4()).replace("-", "")
    created_at: Optional[str] = None
    created_by: Optional[str] = "system"
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
