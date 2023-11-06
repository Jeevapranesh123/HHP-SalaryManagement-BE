from pydantic import BaseModel


class BaseResponse(BaseModel):
    message: str
    status_code: int


class EmployeeResponse(BaseModel):
    employee_id: str
    name: str
    email: str
    phone: str
    password: str


class EmployeeCreateResponse(BaseResponse):
    data: EmployeeResponse


class SalaryResponse(BaseModel):
    employee_id: str
    basic: float
    net_salary: float


class SalaryCreateResponse(BaseResponse):
    data: SalaryResponse
