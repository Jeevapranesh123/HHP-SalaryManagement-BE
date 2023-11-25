from fastapi import APIRouter, Depends, Response, Request

# import DB Utils
from app.database import get_mongo, AsyncIOMotorClient

from app.schemas.request import LeaveCreateRequest, LeaveRespondRequest

from app.schemas.response import (
    PostLeaveResponse,
    RequestLeaveResponse,
    LeaveRespondResponse,
    LeaveHistoryResponse,
)

from app.api.controllers.leave import LeaveController
from app.api.utils.employees import verify_login_token
from app.api.utils.auth import role_required


router = APIRouter()


@router.post("/")
@role_required(["HR", "MD"])
async def post_leave(
    LeaveCreateRequest: LeaveCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    print(LeaveCreateRequest)
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.post_leave(LeaveCreateRequest)
    return PostLeaveResponse(
        message="Leave posted successfully", status_code=200, data=res
    )


@router.post("/request")
async def request_leave(
    LeaveCreateRequest: LeaveCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.request_leave(LeaveCreateRequest)
    return RequestLeaveResponse(
        message="Leave requested successfully", status_code=200, data=res
    )


@router.post("/respond")
@role_required(["HR", "MD"])
async def respond_leave(
    LeaveRespondRequest: LeaveRespondRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.respond_leave(LeaveRespondRequest)
    return LeaveRespondResponse(
        message="Leave responded successfully", status_code=200, data=res
    )


@router.get("/history")
async def get_leave_history(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.get_leave_history(employee_id)
    return LeaveHistoryResponse(
        message="Leave history fetched successfully", status_code=200, data=res
    )


@router.get("/{leave_id}")
async def get_leave(
    leave_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.get_leave(leave_id)
    return LeaveRespondResponse(
        message="Leave fetched successfully", status_code=200, data=res
    )
