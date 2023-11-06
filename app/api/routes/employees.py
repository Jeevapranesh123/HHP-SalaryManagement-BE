from fastapi import APIRouter, Depends, Response, Request

# Import all the Schemas
from app.schemas.request import EmployeeCreateRequest
from app.schemas.response import EmployeeCreateResponse

# import DB Utils
from app.database import get_mongo, AsyncIOMotorClient

# import Controllers
from app.api.controllers import employees as employee_controller


router = APIRouter()


@router.get("/{employee_id}")
async def get_employee(employee_id: str):
    return {"message": "Hello World"}


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
        data=res.model_dump(),
    )
