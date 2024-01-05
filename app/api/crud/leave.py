from app.database import AsyncIOMotorClient
from app.core.config import Config
from fastapi import HTTPException

from app.schemas.leave import LeaveBase, PermissionBase
from app.schemas.db import LeaveInDB, PermissionInDB

import datetime

import uuid

MONGO_DATABASE = Config.MONGO_DATABASE
LEAVE_COLLECTION = Config.LEAVE_COLLECTION


async def get_leave_history(employee_id, status, mongo_client: AsyncIOMotorClient):
    leave_history = (
        await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION]
        .find(
            {"employee_id": employee_id, "leave_type": {"$ne": "permission"}},
            {"_id": 0},
        )
        .sort("requested_at", -1)
        .to_list(length=100)
    )

    if status:
        leave_history = list(filter(lambda x: x["status"] == status, leave_history))

    return leave_history


async def get_leave(leave_id, mongo_client: AsyncIOMotorClient):
    leave = await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].find_one(
        {"id": leave_id, "leave_type": {"$ne": "permission"}}, {"_id": 0}
    )
    if not leave:
        return None

    return leave


async def get_permission_history(employee_id, status, mongo_client: AsyncIOMotorClient):
    permission_history = (
        await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION]
        .find({"employee_id": employee_id, "leave_type": "permission"}, {"_id": 0})
        .sort("requested_at", -1)
        .to_list(length=100)
    )

    if status:
        permission_history = list(
            filter(lambda x: x["status"] == status, permission_history)
        )

    return permission_history


async def get_permission(permission_id, mongo_client: AsyncIOMotorClient):
    permission = await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].find_one(
        {"id": permission_id, "leave_type": "permission"}, {"_id": 0}
    )
    if not permission:
        return None

    return permission


async def request_leave(
    leave: LeaveBase,
    mongo_client: AsyncIOMotorClient,
    type="request",
    requested_by=None,
):
    leave = leave.model_dump()

    leave["id"] = str(uuid.uuid4()).replace("-", "")
    leave["month"] = leave["start_date"].replace(day=1)

    if type == "request":
        leave["requested_by"] = requested_by
        leave["requested_at"] = datetime.datetime.now()
        leave["status"] = "pending"
        leave["remarks"] = ""

    elif type == "post":
        leave["requested_by"] = requested_by
        leave["requested_at"] = datetime.datetime.now()
        leave["status"] = "approved"
        leave["approved_or_rejected_by"] = requested_by
        leave["approved_or_rejected_at"] = datetime.datetime.now()

    leave_in_db = LeaveInDB(**leave)

    if await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].insert_one(
        leave_in_db.model_dump()
    ):
        return leave_in_db.model_dump()


async def respond_leave(leave, mongo_client: AsyncIOMotorClient, responder):
    already_approved_or_rejected = await mongo_client[MONGO_DATABASE][
        LEAVE_COLLECTION
    ].find_one({"id": leave["id"], "status": {"$ne": "pending"}})
    if already_approved_or_rejected:
        raise HTTPException(
            status_code=400,
            detail="Leave has already been approved or rejected",
        )

    data_change = {
        "loss_of_pay": leave["loss_of_pay"],
        "status": leave["status"],
        "remarks": leave["remarks"],
        "approved_or_rejected_at": datetime.datetime.now(),
        "approved_or_rejected_by": responder,
    }

    update = await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].find_one_and_update(
        {"id": leave["id"]}, {"$set": data_change}, return_document=True
    )
    update.pop("_id")
    return update


async def request_permission(
    Permission: PermissionBase,
    mongo_client: AsyncIOMotorClient,
    type="request",
    requested_by=None,
):
    permission = Permission.model_dump()
    permission["id"] = str(uuid.uuid4()).replace("-", "")
    permission["date"] = datetime.datetime.combine(
        permission["start_time"], datetime.time()
    )
    permission["month"] = permission["date"].replace(day=1)
    permission["requested_by"] = requested_by
    permission["requested_at"] = datetime.datetime.now()

    if type == "request":
        permission["status"] = "pending"
        permission["remarks"] = ""

    elif type == "post":
        permission["status"] = "approved"
        permission["approved_or_rejected_by"] = requested_by
        permission["approved_or_rejected_at"] = datetime.datetime.now()

    permission_in_db = PermissionInDB(**permission)

    if await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].insert_one(
        permission_in_db.model_dump()
    ):
        return permission_in_db.model_dump()


async def respond_permission(permission, mongo_client: AsyncIOMotorClient, responder):
    already_approved_or_rejected = await mongo_client[MONGO_DATABASE][
        LEAVE_COLLECTION
    ].find_one({"id": permission["id"], "status": {"$ne": "pending"}})

    if already_approved_or_rejected:
        raise HTTPException(
            status_code=400,
            detail="Permission has already been approved or rejected",
        )

    data_change = {
        "status": permission["status"],
        "remarks": permission["remarks"],
        "approved_or_rejected_at": datetime.datetime.now(),
        "approved_or_rejected_by": responder,
    }

    update = await mongo_client[MONGO_DATABASE][LEAVE_COLLECTION].find_one_and_update(
        {"id": permission["id"]}, {"$set": data_change}, return_document=True
    )

    update.pop("_id")
    return update
