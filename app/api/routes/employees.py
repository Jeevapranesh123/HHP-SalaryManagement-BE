from fastapi import APIRouter, Depends, Response

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


router = APIRouter()


@router.get("/get-branch")
async def get_branch(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    # res = await auth_controller.get_branch(mongo_client, payload)
    res = [
        {"value": "head_office", "label": "Head Office"},
        {"value": "factory", "label": "Factory"},
    ]
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
        "message": "Branch set successfully",
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


@router.get("/")
async def get_all_employees(
    branch: str = None,
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
    payload: dict = Depends(verify_login_token),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    # obj = EmployeeController(payload, mongo_client)
    # res = await obj.get_create_meta()
    # return {
    #     "message": "Success",
    #     "status_code": 200,
    #     "data": res,
    # }

    return {
        "message": "Success",
        "status_code": 200,
        "data": {
            "basic_information": {
                "data": {
                    "employee_id": {"type": "string", "required": True},
                    "name": {"type": "string", "required": True},
                    "email": {"type": "string", "required": True},
                    "phone": {"type": "string", "required": True},
                    "profile_image": {"type": "image", "required": True},
                    "department": {"type": "string"},
                    "designation": {"type": "string"},
                    "branch": {"type": "string", "required": True},
                    "is_marketing_staff": {
                        "type": "radio",
                        "options": [
                            {"label": "Yes", "value": "Yes"},
                            {"label": "No", "value": "No"},
                        ],
                    },
                    "marketing_manager": {"type": "string"},
                },
                "actions": [],
            },
            "bank_details": {
                "data": {
                    "bank_name": {"type": "string"},
                    "account_number": {"type": "string"},
                    "ifsc_code": {"type": "string"},
                    "branch": {"type": "string"},
                    "address": {"type": "string"},
                },
                "actions": [],
            },
            "address": {
                "data": {
                    "address_line_1": {"type": "string"},
                    "address_line_2": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "country": {"type": "string"},
                    "pincode": {"type": "string"},
                },
                "actions": [],
            },
            "govt_id_proofs": {
                "data": {
                    "aadhar": {"type": "string"},
                    "pan": {"type": "string"},
                    "voter_id": {"type": "string"},
                    "driving_license": {"type": "string"},
                    "passport": {"type": "string"},
                },
                "actions": [],
            },
        },
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
