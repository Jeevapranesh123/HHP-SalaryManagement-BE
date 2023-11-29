from app.database import AsyncIOMotorClient
from fastapi import HTTPException

from app.schemas.request import (
    LeaveCreateRequest,
    LeaveRespondRequest,
    PermissionCreateRequest,
    PermissionRespondRequest,
)
from app.schemas.leave import LeaveBase, PermissionBase

from app.api.crud import leave as leave_crud
from app.api.crud import employees as employee_crud

from app.api.lib.Notification import Notification
from app.schemas.notification import NotificationBase


class LeaveController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.employee_id = payload["employee_id"]
        self.employee_role = payload["primary_role"]
        self.mongo_client = mongo_client

    async def get_leave_history(self, employee_id, status):
        if not self.employee_role in ["HR", "MD"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return await leave_crud.get_leave_history(
            employee_id, status, self.mongo_client
        )

    async def get_permission_history(self, employee_id, status):
        if not self.employee_role in ["HR", "MD"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return await leave_crud.get_permission_history(
            employee_id, status, self.mongo_client
        )

    async def get_leave(self, leave_id):
        leave = await leave_crud.get_leave(leave_id, self.mongo_client)
        if not leave:
            raise HTTPException(status_code=404, detail="Leave record not found")
        if (
            not self.employee_role in ["HR", "MD"]
            and leave["employee_id"] != self.employee_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        leave["leave_id"] = leave["id"]
        return leave

    async def get_permission(self, permission_id):
        permission = await leave_crud.get_permission(permission_id, self.mongo_client)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission record not found")
        if (
            not self.employee_role in ["HR", "MD"]
            and permission["employee_id"] != self.employee_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        return permission

    async def post_leave(self, LeaveCreateRequest: LeaveCreateRequest):
        leave_in_create = LeaveBase(**LeaveCreateRequest.model_dump())
        if not await employee_crud.get_employee(
            leave_in_create.employee_id, self.mongo_client
        ):
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(leave_in_create.employee_id),
            )
        res = await leave_crud.request_leave(
            leave_in_create,
            self.mongo_client,
            type="post",
            requested_by=self.employee_id,
        )
        res["leave_id"] = res["id"]

        return res

    async def request_leave(self, LeaveCreateRequest: LeaveCreateRequest):
        leave_in_create = LeaveBase(**LeaveCreateRequest.model_dump())
        if (
            not self.employee_role in ["HR", "MD"]
            and leave_in_create.employee_id != self.employee_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        if not await employee_crud.get_employee(
            leave_in_create.employee_id, self.mongo_client
        ):
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(leave_in_create.employee_id),
            )

        res = await leave_crud.request_leave(
            leave_in_create,
            self.mongo_client,
            type="request",
            requested_by=self.employee_id,
        )
        res["leave_id"] = res["id"]

        return res

    async def respond_leave(self, LeaveRespondRequest: LeaveRespondRequest):
        leave_respond_request = LeaveRespondRequest.model_dump()
        if not await self.get_leave(leave_respond_request["id"]):
            raise HTTPException(status_code=404, detail="Leave record not found")
        return await leave_crud.respond_leave(
            leave_respond_request, self.mongo_client, responder=self.employee_id
        )

    async def post_permission(
        self,
        PermissionCreateRequest: PermissionCreateRequest,
    ):
        permission_in_create = PermissionBase(**PermissionCreateRequest.model_dump())

        if not await employee_crud.get_employee(
            permission_in_create.employee_id, self.mongo_client
        ):
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(
                    permission_in_create.employee_id
                ),
            )
        res = await leave_crud.request_permission(
            permission_in_create,
            self.mongo_client,
            type="post",
            requested_by=self.employee_id,
        )
        res["permission_id"] = res["id"]
        return res

    async def request_permission(
        self,
        PermissionCreateRequest: PermissionCreateRequest,
    ):
        permission_in_create = PermissionBase(**PermissionCreateRequest.model_dump())
        if not await employee_crud.get_employee(
            permission_in_create.employee_id, self.mongo_client
        ):
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(
                    permission_in_create.employee_id
                ),
            )
        if (
            not self.employee_role in ["HR", "MD"]
            and permission_in_create.employee_id != self.employee_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        res = await leave_crud.request_permission(
            permission_in_create,
            self.mongo_client,
            type="request",
            requested_by=self.employee_id,
        )
        res["permission_id"] = res["id"]
        return res

    async def respond_permission(
        self,
        PermissionRespondRequest: PermissionRespondRequest,
    ):
        permission_respond_request = PermissionRespondRequest.model_dump()
        if not await self.get_permission(permission_respond_request["id"]):
            raise HTTPException(status_code=404, detail="Permission record not found")
        return await leave_crud.respond_permission(
            permission_respond_request, self.mongo_client, responder=self.employee_id
        )
