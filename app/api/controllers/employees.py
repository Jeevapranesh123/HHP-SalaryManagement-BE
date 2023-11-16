from fastapi import HTTPException

from app.database import AsyncIOMotorClient

from app.api.utils.employees import validate_new_employee

from app.api.crud import employees as employee_crud
from app.api.controllers import salary as salary_controller

from app.schemas.request import EmployeeCreateRequest
from app.schemas.employees import EmployeeBase

from app.schemas.salary import SalaryBase


async def create_employee(
    employee: EmployeeCreateRequest, mongo_client: AsyncIOMotorClient
):
    is_valid, message = await validate_new_employee(employee, mongo_client)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    emp_in_create = EmployeeBase(**employee.model_dump())

    emp = await employee_crud.create_employee(emp_in_create, mongo_client)

    salary_create_req = SalaryBase(
        employee_id=emp["employee_id"],
        gross=0,
        pf=0,
        esi=0,
    )

    sal = await salary_controller.create_salary(salary_create_req, mongo_client)

    return emp


async def get_employee(employee_id: str, mongo_client: AsyncIOMotorClient):
    return await employee_crud.get_employee(employee_id, mongo_client)


async def get_all_employees(mongo_client: AsyncIOMotorClient):
    return await employee_crud.get_all_employees(mongo_client)
