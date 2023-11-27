from pydantic import BaseModel, root_validator
from app.schemas.salary import SalaryBase
from datetime import datetime


class BaseResponse(BaseModel):
    message: str
    status_code: int


class EmployeeResponse(BaseModel):
    employee_id: str
    name: str
    email: str
    phone: str
    password: str


class EmployeeUpdateRes(BaseModel):
    employee_id: str
    name: str
    email: str
    phone: str


class EmployeeCreateResponse(BaseResponse):
    data: EmployeeResponse


class EmployeeUpdateResponse(BaseResponse):
    data: dict


class SalaryResponse(BaseModel):
    employee_id: str
    gross_salary: float = None
    pf: float = None
    esi: float = None


class MonthlyCompensationResponse(BaseModel):
    employee_id: str
    loss_of_pay: float = None
    leave_cashback: float = None
    last_year_leave_cashback: float = None
    attendance_special_allowance: float = None
    other_special_allowance: float = None
    overtime: float = None


class SalaryIncentivesResponse(BaseModel):
    employee_id: str
    allowance: float = None
    increment: float = None
    bonus: float = None


class PostSalaryResponse(BaseResponse):
    data: SalaryResponse


class PostMonthlyCompensationResponse(BaseResponse):
    data: MonthlyCompensationResponse


class PostSalaryIncentivesResponse(BaseResponse):
    data: SalaryIncentivesResponse


class LeaveResponse(BaseModel):
    type: str
    leave_type: str
    leave_id: str
    employee_id: str
    start_date: str
    end_date: str
    # month: datetime
    # FIXME: Decide whether to send the month in API Response
    no_of_days: int
    status: str
    reason: str
    remarks: str

    @root_validator(pre=True)
    def convert_date_to_str(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")
        values["start_date"] = datetime.strftime(start_date, "%Y-%m-%d")
        values["end_date"] = datetime.strftime(end_date, "%Y-%m-%d")
        return values


class PermissionResponse(BaseModel):
    permission_id: str
    employee_id: str
    date: str
    start_time: str
    end_time: str
    no_of_hours: float
    status: str
    reason: str
    remarks: str

    @root_validator(pre=True)
    def convert_date_to_str(cls, values):
        date = values.get("date")
        values["date"] = datetime.strftime(date, "%Y-%m-%d")
        values["start_time"] = datetime.strftime(values.get("start_time"), "%H:%M:%S")
        values["end_time"] = datetime.strftime(values.get("end_time"), "%H:%M:%S")
        return values


class PostLeaveResponse(BaseResponse):
    data: LeaveResponse


class RequestLeaveResponse(BaseResponse):
    data: LeaveResponse


class LeaveRespondResponse(BaseResponse):
    data: LeaveResponse


class GetLeaveResponse(BaseResponse):
    data: dict


class LeaveHistoryResponse(BaseResponse):
    data: list


class PostPermissionResponse(BaseResponse):
    message: str = "Permission posted successfully"
    data: PermissionResponse


class RequestPermissionResponse(BaseResponse):
    message: str = "Permission requested successfully"
    data: PermissionResponse


class PermissionRespondResponse(BaseResponse):
    message: str = "Permission responded successfully"
    data: PermissionResponse


class GetPermissionResponse(BaseResponse):
    data: dict


class PermissionHistoryResponse(BaseResponse):
    message: str = "Permission history retrieved successfully"
    data: list


class SalaryAdvanceResponse(BaseModel):
    salary_advance_id: str
    employee_id: str
    amount: float
    month: str
    status: str
    remarks: str
    data_changed: bool = None

    @root_validator(pre=True)
    def convert_date_to_str(cls, values):
        date = values.get("month")
        values["month"] = datetime.strftime(date, "%Y-%m-%d")
        return values


class PostSalaryAdvanceResponse(BaseResponse):
    data: SalaryAdvanceResponse


class RequestSalaryAdvanceResponse(BaseResponse):
    data: SalaryAdvanceResponse


class SalaryAdvanceRespondResponse(BaseResponse):
    data: SalaryAdvanceResponse


class LoanResponse(BaseModel):
    loan_id: str
    employee_id: str
    amount: float
    month: str
    emi: float
    tenure: int
    status: str
    remarks: str

    @root_validator(pre=True)
    def convert_date_to_str(cls, values):
        date = values.get("month")
        values["month"] = datetime.strftime(date, "%Y-%m-%d")
        return values


class PostLoanResponse(BaseResponse):
    data: LoanResponse


class RequestLoanResponse(BaseResponse):
    data: LoanResponse


class LoanRespondResponse(BaseResponse):
    data: LoanResponse


class LoanHistoryResponse(BaseResponse):
    data: list
