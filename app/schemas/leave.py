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
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class LeaveBase(BaseModel):
    employee_id: str
    type: LeaveType
    month: LeaveMonth
    start_date: datetime.date
    end_date: datetime.date
    no_of_days: int
    reason: str

    @root_validator(pre=True)
    def calculate_no_of_days(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")
        if start_date > end_date:
            raise ValueError("start_date must be less than end_date")
        if start_date and end_date:
            values["no_of_days"] = (
                datetime.datetime.strptime(str(end_date), "%Y-%m-%d").day
                - datetime.datetime.strptime(str(start_date), "%Y-%m-%d").day
            )

        values["status"] = "pending"

        return values


class PermissionBase(BaseModel):
    employee_id: str
    type: str = "permission"
    date: datetime.date
    start_time: datetime.datetime
    end_time: datetime.datetime
    no_of_hours: int
    reason: str

    @root_validator(pre=True)
    def calculate_no_of_hours(cls, values):
        start_time = values.get("start_time")
        end_time = values.get("end_time")
        # Ensure start_time and end_time are datetime.datetime objects
        if isinstance(start_time, str):
            try:
                start_time = datetime.datetime.fromisoformat(start_time)
                values["start_time"] = start_time  # Update the values dictionary
            except ValueError:
                raise ValidationError(f"Invalid start_time format: {start_time}")

        if isinstance(end_time, str):
            try:
                end_time = datetime.datetime.fromisoformat(end_time)
                values["end_time"] = end_time  # Update the values dictionary
            except ValueError:
                raise ValidationError(f"Invalid end_time format: {end_time}")

        if start_time > end_time:
            raise ValueError("start_time must be less than end_time")
        if start_time and end_time:
            values["no_of_hours"] = (end_time - start_time).seconds // 3600

        values["status"] = "pending"

        return values
