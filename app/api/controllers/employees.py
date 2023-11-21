from fastapi import HTTPException

from app.database import AsyncIOMotorClient

from app.api.utils.employees import validate_new_employee, validate_update_employee

from app.api.crud import employees as employee_crud
from app.api.controllers import salary as salary_controller

from app.schemas.request import EmployeeCreateRequest, EmployeeUpdateRequest
from app.schemas.employees import EmployeeBase

from app.schemas.salary import SalaryBase

from pydantic import BaseModel, create_model
from typing import Optional, List, Type


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


async def get_employee(
    employee_id: str, formatted: bool, mongo_client: AsyncIOMotorClient
):
    emp = await employee_crud.get_employee_with_salary(employee_id, mongo_client)
    if formatted:
        res = {
            "information": {
                "employee_id": "EMP67890",
                "name": "Alice Smith",
                "email": "alicesmith@example.com",
                "phone": "9876543210",
                "department": "Human Resources",
                "designation": "HR Manager",
            },
            "bank_details": emp["bank_details"],
            "address": emp["address"],
            "govt_id_proofs": emp["govt_id_proofs"],
            "salary_details": {
                "gross_salary": emp["gross_salary"],
                "pf": emp["pf"],
                "esi": emp["esi"],
                "net_salary": emp["net_salary"],
            },
        }

        return res

    return emp


async def get_all_employees(mongo_client: AsyncIOMotorClient):
    return await employee_crud.get_all_employees(mongo_client)


async def update_employee(
    employee_id,
    employee_details: EmployeeUpdateRequest,
    mongo_client: AsyncIOMotorClient,
):
    emp_in_update = EmployeeUpdateRequest(**employee_details.model_dump())

    emp_in_update = emp_in_update.model_dump(exclude_none=True)
    print(emp_in_update)
    emp = await employee_crud.get_employee(employee_id, mongo_client)

    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    is_valid, message = await validate_update_employee(
        employee_id, employee_details, mongo_client
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    # FIXME: Update salary if needed
    emp = await employee_crud.update_employee(employee_id, emp_in_update, mongo_client)

    return emp


# # Function to get fields of a Pydantic model, including nested fields
# # Function to get fields of a Pydantic model, including nested fields
# def get_model_fields(model: Type[BaseModel], prefix: str = '') -> List[str]:
#     fields = []
#     for field_name, field_model in model.__fields__.items():
#         if issubclass(field_model.type_, BaseModel):
#             # Recursive call for nested fields
#             nested_model = create_model(field_name, **{f.name: (f.outer_type_, ...) for f in field_model.type_.__fields__.values()})
#             fields.extend(get_model_fields(nested_model, prefix=f"{prefix}{field_name}."))
#         else:
#             fields.append(f"{prefix}{field_name}")
#     return fields

# # Function to get editable fields
# def get_editable_fields() -> List[str]:
#     all_fields = get_model_fields(EmployeeBase)
#     # Exclude non-editable fields
#     editable_fields = [field for field in all_fields if field not in ["phone", "email"]]
#     return editable_fields


async def get_editable_fields():
    # return ["name", "department", "designation", "bank_details", "address", "govt_id_proofs"]

    return [
        {"name": True},
        {"phone": True},
        {"department": True},
        {"designation": True},
        {
            "bank_details": {
                "bank_name": True,
                "account_number": True,
                "ifsc_code": True,
                "branch": True,
                "address": True,
            }
        },
        {
            "address": {
                "address_line_1": True,
                "address_line_2": True,
                "city": True,
                "state": True,
                "country": True,
                "pincode": True,
            }
        },
        {
            "govt_id_proofs": {
                "aadhar": True,
                "pan": True,
                "voter_id": True,
                "driving_license": True,
                "passport": True,
            }
        },
    ]


async def get_create_required_fields():
    # return ["name", "department", "designation", "bank_details", "address", "govt_id_proofs"]

    return [
        {"employee_id": True},
        {"name": True},
        {"email": True},
        {"phone": True},
    ]
