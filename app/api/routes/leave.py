from fastapi import APIRouter, Depends, Response, Request

# import DB Utils
from app.database import get_mongo, AsyncIOMotorClient

from app.schemas.request import (
    LeaveCreateRequest,
    LeaveRespondRequest,
    PermissionCreateRequest,
    PermissionRespondRequest,
)

from app.api.controllers import leave as leave_controller

router = APIRouter()


@router.post("/")
async def request_leave(
    LeaveCreateRequest: LeaveCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await leave_controller.request_leave(LeaveCreateRequest, mongo_client)


@router.post("/respond")
async def respond_leave(
    LeaveRespondRequest: LeaveRespondRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await leave_controller.respond_leave(LeaveRespondRequest, mongo_client)


@router.post("/request_permission")
async def request_permission(
    PermissionCreateRequest: PermissionCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await leave_controller.request_permission(
        PermissionCreateRequest, mongo_client
    )


@router.post("/respond_permission")
async def respond_permission(
    PermissionRespondRequest: PermissionRespondRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await leave_controller.respond_permission(
        PermissionRespondRequest, mongo_client
    )
