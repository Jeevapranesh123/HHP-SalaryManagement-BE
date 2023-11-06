from app.database import AsyncIOMotorClient
from app.core.config import Config

from app.schemas.leave import LeaveBase, PermissionBase
from app.schemas.db import LeaveInDB, PermissionInDB

import datetime

import uuid

MONGO_DATABASE = Config.MONGO_DATABASE
LEAVE_COLLECTION = Config.LEAVE_COLLECTION


async def request_leave(leave: LeaveBase, mongo_client: AsyncIOMotorClient):
    leave = leave.model_dump()

    leave["id"] = str(uuid.uuid4()).replace("-", "")

    leave_in_db = LeaveInDB(**leave)

    if await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].insert_one(
        leave_in_db.model_dump()
    ):
        return leave_in_db


async def respond_leave(leave, mongo_client: AsyncIOMotorClient):
    leave = leave.model_dump()

    data_change = {
        "status": leave["status"],
        "remarks": leave["remarks"],
        "approved_or_rejected_at": datetime.datetime.now(),
    }

    if await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].update_one(
        {"id": leave["leave_id"]},
        {"$set": data_change},
    ):
        return leave


async def request_permission(
    Permission: PermissionBase, mongo_client: AsyncIOMotorClient
):
    permission = Permission.model_dump()

    permission["id"] = str(uuid.uuid4()).replace("-", "")
    permission["date"] = datetime.datetime.combine(permission["date"], datetime.time())
    permission_in_db = PermissionInDB(**permission)

    if await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].insert_one(
        permission_in_db.model_dump()
    ):
        return permission_in_db


async def respond_permission(permission, mongo_client: AsyncIOMotorClient):
    permission = permission.model_dump()

    data_change = {
        "status": permission["status"],
        "remarks": permission["remarks"],
        "approved_or_rejected_at": datetime.datetime.now(),
    }

    if await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].update_one(
        {"id": permission["permission_id"]},
        {"$set": data_change},
    ):
        return permission
