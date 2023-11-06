from app.database import AsyncIOMotorClient

from app.schemas.request import (
    LeaveCreateRequest,
    LeaveRespondRequest,
    PermissionCreateRequest,
    PermissionRespondRequest,
)
from app.schemas.leave import LeaveBase, PermissionBase

from app.api.crud import leave as leave_crud


async def request_leave(
    LeaveCreateRequest: LeaveCreateRequest,
    mongo_client: AsyncIOMotorClient,
):
    print(LeaveCreateRequest.model_dump())
    leave_in_create = LeaveBase(**LeaveCreateRequest.model_dump())
    return await leave_crud.request_leave(leave_in_create, mongo_client)


async def respond_leave(
    LeaveRespondRequest: LeaveRespondRequest,
    mongo_client: AsyncIOMotorClient,
):
    print(LeaveRespondRequest.model_dump())
    return await leave_crud.respond_leave(LeaveRespondRequest, mongo_client)


async def request_permission(
    PermissionCreateRequest: PermissionCreateRequest,
    mongo_client: AsyncIOMotorClient,
):
    print(PermissionCreateRequest.model_dump())
    permission_in_create = PermissionBase(**PermissionCreateRequest.model_dump())
    return await leave_crud.request_permission(permission_in_create, mongo_client)


async def respond_permission(
    PermissionRespondRequest: PermissionRespondRequest,
    mongo_client: AsyncIOMotorClient,
):
    print(PermissionRespondRequest.model_dump())
    return await leave_crud.respond_permission(PermissionRespondRequest, mongo_client)
