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


class EmployeeUpdateRes(BaseModel):
    employee_id: str
    name: str
    email: str
    phone: str


class EmployeeCreateResponse(BaseResponse):
    data: EmployeeResponse


class EmployeeUpdateResponse(BaseResponse):
    data: EmployeeUpdateRes


class SalaryResponse(BaseModel):
    employee_id: str
    gross: float


class SalaryCreateResponse(BaseResponse):
    data: SalaryResponse
