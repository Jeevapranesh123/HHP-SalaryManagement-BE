from pydantic import BaseModel, Field
from typing import Optional

import datetime
import uuid


class AttendanceBase(BaseModel):
    employee_id: str
    date: datetime.datetime
    status: str


class AttendanceInDB(AttendanceBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace("-", ""))
    created_at: Optional[datetime.datetime] = datetime.datetime.now()
    created_by: Optional[str] = "system"
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
