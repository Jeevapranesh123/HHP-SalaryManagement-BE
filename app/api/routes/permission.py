from fastapi import APIRouter, Depends, Response, Request

# import DB Utils
from app.database import get_mongo, AsyncIOMotorClient

from app.schemas.request import PermissionCreateRequest, PermissionRespondRequest

from app.schemas.response import (
    PostPermissionResponse,
    RequestPermissionResponse,
    PermissionRespondResponse,
    PermissionHistoryResponse,
    GetPermissionResponse,
)

from app.api.controllers.leave import LeaveController

from app.api.utils.employees import verify_login_token
from app.api.utils.auth import role_required


router = APIRouter()


@router.post("/")
@role_required(["HR", "MD"])
async def post_permission(
    PermissionCreateRequest: PermissionCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.post_permission(PermissionCreateRequest, mongo_client)
    return PostPermissionResponse(
        message="Permission posted successfully", status_code=201, data=res
    )


@router.post("/request")
async def request_permission(
    PermissionCreateRequest: PermissionCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.request_permission(
        PermissionCreateRequest, mongo_client
    )
    return RequestPermissionResponse(
        message="Permission requested successfully", status_code=201, data=res
    )


@router.post("/respond")
@role_required(["HR", "MD"])
async def respond_permission(
    PermissionRespondRequest: PermissionRespondRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.respond_permission(
        PermissionRespondRequest, mongo_client
    )
    return PermissionRespondResponse(
        message="Permission responded successfully", status_code=201, data=res
    )


@router.get("/history")
async def get_permission_history(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.get_permission_history(employee_id, mongo_client)
    return PermissionHistoryResponse(
        message="Permission history retrieved successfully", status_code=200, data=res
    )


@router.get("/{permission_id}")
async def get_permission(
    permission_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.get_permission(permission_id, mongo_client)
    return GetPermissionResponse(
        message="Permission history retrieved successfully", status_code=200, data=res
    )
