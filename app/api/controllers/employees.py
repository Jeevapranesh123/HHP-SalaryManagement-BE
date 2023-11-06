from fastapi import HTTPException

from app.database import AsyncIOMotorClient

from app.api.utils.employees import validate_new_employee

from app.api.crud import employees as employee_crud

from app.schemas.request import EmployeeCreateRequest
from app.schemas.employees import EmployeeBase


async def create_employee(
    employee: EmployeeCreateRequest, mongo_client: AsyncIOMotorClient
):
    is_valid, message = await validate_new_employee(employee, mongo_client)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    emp_in_create = EmployeeBase(**employee.model_dump())

    return await employee_crud.create_employee(emp_in_create, mongo_client)
