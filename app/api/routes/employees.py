from fastapi import APIRouter, Depends, Response

# Import all the Schemas
from app.schemas.request import EmployeeCreateRequest, EmployeeUpdateRequest
from app.schemas.response import EmployeeCreateResponse, EmployeeUpdateResponse

# import DB Utils
from app.database import get_mongo, AsyncIOMotorClient

# import Controllers
from app.api.controllers.employees import EmployeeController
from app.api.utils.employees import verify_login_token, verify_custom_master_token


router = APIRouter()


@router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    formatted: bool = False,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    obj = EmployeeController(payload, mongo_client)
    res = await obj.get_employee(employee_id)

    return {
        "message": "Success",
        "status_code": 200,
        "data": res,
    }


@router.get("/")
async def get_all_employees(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    obj = EmployeeController(payload, mongo_client)
    res = await obj.get_all_employees()

    return {
        "message": "Success",
        "status_code": 200,
        "data": res,
    }


@router.post("/create", status_code=201)
async def create(
    employee: EmployeeCreateRequest,
    response: Response,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_custom_master_token),
):
    obj = EmployeeController(payload, mongo_client)
    res = await obj.create_employee(employee)

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
    payload: dict = Depends(verify_login_token),
):
    obj = EmployeeController(payload, mongo_client)
    res = await obj.update_employee(employee_id, employee_details)

    return EmployeeUpdateResponse(
        message="Employee Updated Successfully", status_code=200, data=res
    )


@router.get("/info/editable")
async def get_editable_fields(
    payload: dict = Depends(verify_login_token),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    obj = EmployeeController(payload, mongo_client)
    res = await obj.get_editable_fields()

    return {
        "message": "Success",
        "status_code": 200,
        "data": res,
    }


@router.get("/info/create-required")
async def get_create_required_fields(
    payload: dict = Depends(verify_login_token),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    obj = EmployeeController(payload, mongo_client)
    res = await obj.get_create_required_fields()
    return {
        "message": "Success",
        "status_code": 200,
        "data": res,
    }
