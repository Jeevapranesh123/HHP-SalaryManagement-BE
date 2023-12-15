from fastapi import APIRouter, Depends, Response, BackgroundTasks

# Import all the Schemas
from app.schemas.request import EmployeeCreateRequest, EmployeeUpdateRequest
from app.schemas.response import EmployeeCreateResponse, EmployeeUpdateResponse

# import DB Utils
from app.database import get_mongo, AsyncIOMotorClient

# import Controllers
from app.api.controllers.employees import EmployeeController
from app.api.utils.employees import verify_login_token, verify_custom_master_token

# import UploadFile
from fastapi import UploadFile, File

from app.core.config import Config


router = APIRouter()


@router.get("/get-branch")
async def get_branch(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    obj = EmployeeController(payload, mongo_client)

    res = await obj.get_branch()

    return {
        "message": "Branch fetched successfully",
        "status_code": 200,
        "data": res,
    }


@router.post("/set-branch")
async def set_branch(
    branch: str,
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    obj = EmployeeController(payload, mongo_client)

    res = await obj.set_branch(employee_id, branch)

    return {
        "message": "Branch changed to " + branch,
        "status_code": 200,
        "data": res,
    }


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


@router.get("")
async def get_all_employees(
    role: bool = None,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    obj = EmployeeController(payload, mongo_client)
    res = await obj.get_all_employees(role=role)

    return {
        "message": "Success",
        "status_code": 200,
        "data": res,
    }


@router.post("/create", status_code=201)
async def create(
    employee: EmployeeCreateRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_custom_master_token),
):
    obj = EmployeeController(payload, mongo_client)
    res = await obj.create_employee(employee, background_tasks)

    return EmployeeCreateResponse(
        message="Employee Created Successfully",
        status_code=201,
        data=res,
    )


@router.post("/profile_image")
async def upload_profile_image(
    employee_id: str,
    profile_image: UploadFile = File(...),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    obj = EmployeeController(payload, mongo_client)
    res = await obj.upload_profile_image(employee_id, profile_image)

    return {
        "message": "Profile Image Uploaded Successfully",
        "status_code": 200,
        "data": res,
    }


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


@router.get("/info/create-meta")
async def get_create_meta(
    type: str = None,
    payload: dict = Depends(verify_login_token),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    obj = EmployeeController(payload, mongo_client)

    data = await obj.get_create_meta(type)

    return {
        "message": "Success",
        "status_code": 200,
        "data": data,
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
