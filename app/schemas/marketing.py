from pydantic import BaseModel, root_validator, validator
import uuid
import datetime
from typing import Optional
from enum import Enum


class TypeEnum(str, Enum):
    check_in = "check_in"
    check_out = "check_out"
    visit = "visit"
    meeting = "meeting"
    other = "other"


class LocationEntry(BaseModel):
    employee_id: str
    type: TypeEnum = TypeEnum.check_in
    date: datetime.date = datetime.date.today()
    time: datetime.time = datetime.datetime.now().replace(microsecond=0).time()
    campaign_description: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    latitude: float
    longitude: float
    category: Optional[str] = None


class LocationEntryInDB(LocationEntry):
    date: datetime.datetime
    time: datetime.datetime
    id: str = str(uuid.uuid4()).replace("-", "")
    created_at: Optional[datetime.datetime] = datetime.datetime.now()
    created_by: Optional[str] = "system"
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    @root_validator(pre=True)
    def set_time_and_date(cls, values):
        time = values.get("time")
        date = values.get("date")

        values["date"] = datetime.datetime.combine(date, datetime.time.min)
        values["time"] = datetime.datetime.combine(date, time)

        return values
