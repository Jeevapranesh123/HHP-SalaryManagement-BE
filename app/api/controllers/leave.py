from app.database import AsyncIOMotorClient
from fastapi import HTTPException

from app.schemas.request import (
    LeaveCreateRequest,
    LeaveRespondRequest,
    PermissionCreateRequest,
    PermissionRespondRequest,
    LateEntryCreateRequest,
)
from app.schemas.leave import LeaveBase, PermissionBase, LateEntryBase

from app.api.crud import leave as leave_crud
from app.api.crud import employees as employee_crud
from app.api.crud import auth as auth_crud

from app.api.lib.Notification import Notification
from app.schemas.notification import (
    NotificationBase,
    SendNotification,
    NotificationMeta,
)


class LeaveController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.employee_id = payload["employee_id"]
        self.employee_role = payload["primary_role"]
        self.employee_name = payload["employee_name"]
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
        emp = await employee_crud.get_employee(
            leave_in_create.employee_id, self.mongo_client
        )
        if not emp:
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

        user = await auth_crud.get_user_with_employee_id(
            leave_in_create.employee_id, self.mongo_client
        )

        branch = emp["branch"]

        notification = Notification(
            self.employee_id, "request_leave", self.mongo_client
        )

        notifiers = [res["employee_id"], "HR", "MD"]

        emp_notification = NotificationBase(
            title="Leave Approved",
            description="Leave has been approved for you",
            payload={"url": "/leave/history?tab=leave"},
            ui_action="action",
            type="leave",
            source="leave_request",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        hr_notification = NotificationBase(
            title="Leave Approved",
            description="{} has approved a leave".format(self.employee_name),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=leave&tab=leave".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="HR_{}".format(format(branch.replace(" ", "_"))),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Leave Approved",
            description="{} has approved a leave".format(self.employee_name),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=leave&tab=leave".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = []

        # if self.employee_role == "HR":
        #     notifier = [emp_notification, md_notification]

        # elif self.employee_role == "MD":
        #     notifier = [emp_notification, hr_notification]

        notifier = [emp_notification]

        send = SendNotification(notifier=notifier)

        await notification.send_notification(send)

        return res

    async def request_leave(self, LeaveCreateRequest: LeaveCreateRequest):
        leave_in_create = LeaveBase(**LeaveCreateRequest.model_dump())
        if (
            not self.employee_role in ["HR", "MD"]
            and leave_in_create.employee_id != self.employee_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        emp = await employee_crud.get_employee(
            leave_in_create.employee_id, self.mongo_client
        )
        if not emp:
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

        user = await auth_crud.get_user_with_employee_id(
            leave_in_create.employee_id, self.mongo_client
        )

        branch = emp["branch"]

        notification = Notification(
            self.employee_id, "request_leave", self.mongo_client
        )
        notifiers = [res["employee_id"], "HR", "MD"]

        emp_notification = NotificationBase(
            title="Leave Request",
            description="Leave has been requested for you by {}".format(
                self.employee_name
            ),
            payload={"url": "/leave/history?tab=leave"},
            ui_action="action",
            type="leave",
            source="leave_request",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        hr_notification = NotificationBase(
            title="Leave Request",
            description="{} has requested leave".format(user["info"]["name"]),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=leave&tab=leave".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="HR_{}".format(format(branch.replace(" ", "_"))),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Leave Request",
            description="{} has requested leave".format(user["info"]["name"]),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=leave&tab=leave".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = []

        if self.employee_role == "HR":
            notifier = [emp_notification, md_notification]

        elif self.employee_role == "MD":
            notifier = [emp_notification, hr_notification]

        elif self.employee_role == "employee":
            notifier = [hr_notification, md_notification]

        send = SendNotification(notifier=notifier)

        await notification.send_notification(send)

        return res

    async def respond_leave(self, LeaveRespondRequest: LeaveRespondRequest):
        leave_respond_request = LeaveRespondRequest.model_dump()
        if not await self.get_leave(leave_respond_request["id"]):
            raise HTTPException(status_code=404, detail="Leave record not found")
        res = await leave_crud.respond_leave(
            leave_respond_request, self.mongo_client, responder=self.employee_id
        )

        user = await auth_crud.get_user_with_employee_id(
            res["employee_id"], self.mongo_client
        )

        branch = user["info"]["branch"]

        notification = Notification(
            self.employee_id, "request_leave", self.mongo_client
        )

        notifiers = [res["employee_id"], "HR", "MD"]

        emp_notification = NotificationBase(
            title="Leave {}".format(res["status"].capitalize()),
            description="Your leave request has been {}".format(res["status"]),
            payload={"url": "/leave/history?tab=leave"},
            ui_action="action",
            type="leave",
            source="leave_request",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        hr_notification = NotificationBase(
            title="Leave {}".format(res["status"].capitalize()),
            description="{} has {} a leave request".format(
                self.employee_name, res["status"]
            ),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=leave&tab=leave".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="HR_{}".format(format(branch.replace(" ", "_"))),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Leave Approved",
            description="{} has {} a leave request".format(
                self.employee_name, res["status"]
            ),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=leave&tab=leave".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = []

        # if self.employee_role == "HR":
        #     notifier = [emp_notification, md_notification]

        # elif self.employee_role == "MD":
        #     notifier = [emp_notification, hr_notification]

        notifier = [emp_notification]

        send = SendNotification(notifier=notifier)

        await notification.send_notification(send)

        return res

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

        user = await auth_crud.get_user_with_employee_id(
            permission_in_create.employee_id, self.mongo_client
        )

        branch = user["info"]["branch"]

        notification = Notification(
            self.employee_id, "request_leave", self.mongo_client
        )

        notifiers = [res["employee_id"], "HR", "MD"]

        emp_notification = NotificationBase(
            title="Permission Approved",
            description="Permission has been approved for you",
            payload={"url": "/leave/history?tab=permission"},
            ui_action="action",
            type="leave",
            source="leave_request",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        hr_notification = NotificationBase(
            title="Permission Approved",
            description="{} has approved a permission".format(self.employee_name),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=permission&tab=permission".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="HR_{}".format(format(branch.replace(" ", "_"))),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Permission Approved",
            description="{} has approved a permission".format(self.employee_name),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=permission&tab=permission".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = []

        # if self.employee_role == "HR":
        #     notifier = [emp_notification, md_notification]

        # elif self.employee_role == "MD":
        #     notifier = [emp_notification, hr_notification]

        notifier = [emp_notification]
        send = SendNotification(notifier=notifier)

        await notification.send_notification(send)

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

        user = await auth_crud.get_user_with_employee_id(
            permission_in_create.employee_id, self.mongo_client
        )

        branch = user["info"]["branch"]

        notification = Notification(
            self.employee_id, "request_leave", self.mongo_client
        )

        notifiers = [res["employee_id"], "HR", "MD"]

        emp_notification = NotificationBase(
            title="Permission Request",
            description="Permission has been requested for you by {}".format(
                self.employee_name
            ),
            payload={"url": "/leave/history?tab=permission"},
            ui_action="action",
            type="leave",
            source="leave_request",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        hr_notification = NotificationBase(
            title="Permission Request",
            description="{} has requested permission".format(user["info"]["name"]),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=permission&tab=permission".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="HR_{}".format(format(branch.replace(" ", "_"))),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Permission Request",
            description="{} has requested permission".format(user["info"]["name"]),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=permission&tab=permission".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = []

        if self.employee_role == "HR":
            notifier = [emp_notification, md_notification]

        elif self.employee_role == "MD":
            notifier = [emp_notification, hr_notification]

        elif self.employee_role == "employee":
            notifier = [hr_notification, md_notification]

        send = SendNotification(notifier=notifier)

        await notification.send_notification(send)

        return res

    async def respond_permission(
        self,
        PermissionRespondRequest: PermissionRespondRequest,
    ):
        permission_respond_request = PermissionRespondRequest.model_dump()
        if not await self.get_permission(permission_respond_request["id"]):
            raise HTTPException(status_code=404, detail="Permission record not found")
        res = await leave_crud.respond_permission(
            permission_respond_request, self.mongo_client, responder=self.employee_id
        )

        user = await auth_crud.get_user_with_employee_id(
            res["employee_id"], self.mongo_client
        )

        branch = user["info"]["branch"]

        notification = Notification(
            self.employee_id, "request_leave", self.mongo_client
        )

        notifiers = [res["employee_id"], "HR", "MD"]

        emp_notification = NotificationBase(
            title="Permission {}".format(res["status"].capitalize()),
            description="Your permission request has been {}".format(res["status"]),
            payload={"url": "/leave/history?tab=permission"},
            ui_action="action",
            type="leave",
            source="leave_request",
            target="{}".format(res["employee_id"]),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        hr_notification = NotificationBase(
            title="Permission {}".format(res["status"].capitalize()),
            description="{} has {} a permission request".format(
                self.employee_name, res["status"]
            ),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=permission&tab=permission".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="HR_{}".format(format(branch.replace(" ", "_"))),
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        md_notification = NotificationBase(
            title="Permission {}".format(res["status"].capitalize()),
            description="{} has {} a permission request".format(
                self.employee_name, res["status"]
            ),
            payload={
                "url": "/employees/{}/leave/respond?id={}&type=permission&tab=permission".format(
                    res["employee_id"], res["id"]
                )
            },
            ui_action="action",
            type="leave",
            source="leave_request",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=self.employee_id,
            ),
        )

        notifier = []

        # if self.employee_role == "HR":
        #     notifier = [emp_notification, md_notification]

        # elif self.employee_role == "MD":
        #     notifier = [emp_notification, hr_notification]

        notifier = [emp_notification]

        send = SendNotification(notifier=notifier)

        await notification.send_notification(send)

        return res

    async def post_late_entry(self, LateEntryCreateRequest: LateEntryCreateRequest):
        late_entry_in_create = LateEntryBase(**LateEntryCreateRequest.model_dump())

        emp = await employee_crud.get_employee(
            late_entry_in_create.employee_id, self.mongo_client
        )

        if not emp:
            raise HTTPException(
                status_code=404,
                detail="Employee '{}' not found".format(
                    late_entry_in_create.employee_id
                ),
            )

        res = await leave_crud.post_late_entry(
            late_entry_in_create,
            self.mongo_client,
            posted_by=self.employee_id,
        )

        return res
