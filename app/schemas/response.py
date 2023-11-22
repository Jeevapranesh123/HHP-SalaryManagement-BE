from pydantic import BaseModel
from app.schemas.salary import SalaryBase


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
