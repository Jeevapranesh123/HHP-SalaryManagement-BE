from fastapi import APIRouter, Depends, Response, Request

# Import all the Schemas
from app.schemas.request import EmployeeCreateRequest, EmployeeUpdateRequest
from app.schemas.response import EmployeeCreateResponse, EmployeeUpdateResponse

# import DB Utils
from app.database import get_mongo, AsyncIOMotorClient

# import Controllers
from app.api.controllers import employees as employee_controller


router = APIRouter()


@router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    formatted: bool = False,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await employee_controller.get_employee(employee_id, formatted, mongo_client)
    # return res
    return {
        "message": "Success",
        "status_code": 200,
        "data": res,
    }


@router.get("/")
async def get_all_employees(mongo_client: AsyncIOMotorClient = Depends(get_mongo)):
    res = await employee_controller.get_all_employees(mongo_client)

    return {
        "message": "Success",
        "status_code": 200,
        "data": res,
    }


@router.post("/create", response_model=EmployeeCreateResponse, status_code=201)
async def create(
    employee: EmployeeCreateRequest,
    response: Response,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await employee_controller.create_employee(employee, mongo_client)

    return EmployeeCreateResponse(
        message="Employee Created Successfully",
        status_code=201,
        data=res,
    )


@router.put("/update")
async def update(
    employee_id: str,
    employee_details: EmployeeUpdateRequest,
    response: Response,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await employee_controller.update_employee(
        employee_id, employee_details, mongo_client
    )

    return EmployeeUpdateResponse(
        message="Employee Updated Successfully", status_code=200, data=res
    )
