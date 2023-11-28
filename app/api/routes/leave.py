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
from app.schemas.employees import StatusEnum


router = APIRouter()


@router.get("/meta")
async def get_meta(
    access_type: str,
    type: str = None,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    leave_respond_action = [
        {
            "label": "Approve",
            "type": "button",
            "variant": "success",
            "action": {"url": "/leave/respond", "method": "POST"},
            "body": {"status": "approved"},
        },
        {
            "label": "Reject",
            "type": "button",
            "variant": "destructive",
            "action": {"url": "/leave/respond", "method": "POST"},
            "body": {"status": "rejected"},
        },
    ]

    permission_respond_action = [
        {
            "label": "Approve",
            "type": "button",
            "variant": "success",
            "action": {"url": "/permission/respond", "method": "POST"},
            "body": {"status": "approved"},
        },
        {
            "label": "Reject",
            "type": "button",
            "variant": "destructive",
            "action": {"url": "/permission/respond", "method": "POST"},
            "body": {"status": "rejected"},
        },
    ]

    leave_request_action = [
        {
            "label": "Request",
            "type": "button",
            "variant": "default",
            "action": {"url": "/leave/request", "method": "POST"},
        }
    ]

    permission_request_action = [
        {
            "label": "Request",
            "type": "button",
            "variant": "default",
            "action": {"url": "/permission/request", "method": "POST"},
        }
    ]

    leave_post_action = [
        {
            "label": "Submit",
            "type": "button",
            "variant": "default",
            "action": {"url": "/leave/", "method": "POST"},
        }
    ]

    permission_post_action = [
        {
            "label": "Submit",
            "type": "button",
            "variant": "default",
            "action": {"url": "/permission/", "method": "POST"},
        }
    ]

    data = {
        "message": "Leave meta fetched successfully",
        "status_code": 200,
        "data": {
            "type": {
                "leave": {
                    "data": {
                        "employee_id": {
                            "type": "string",
                            "required": True,
                        },
                        "leave_type": {
                            "type": "dropdown",
                            "options": [
                                {"label": "Casual", "value": "casual"},
                                {"label": "Medical", "value": "medical"},
                            ],
                            "required": True,
                        },
                        "start_date": {
                            "type": "date",
                            "format": "YYYY-MM-DD",
                            "required": True,
                        },
                        "end_date": {
                            "type": "date",
                            "format": "YYYY-MM-DD",
                            "required": False,
                        },
                        "no_of_days": {"type": "number", "required": True},
                        "reason": {"type": "textarea", "required": True},
                        "remarks": {"type": "textarea", "required": True},
                    },
                },
                "permission": {
                    "data": {
                        "employee_id": {
                            "type": "string",
                            "required": True,
                        },
                        "leave_type": {
                            "type": "dropdown",
                            "options": [
                                {"label": "Permission", "value": "permission"},
                            ],
                            "required": True,
                        },
                        "date": {
                            "type": "date",
                            "format": "YYYY-MM-DD",
                            "required": True,
                        },
                        "start_time": {
                            "type": "time",
                            "format": "HH:MM",
                            "required": True,
                        },
                        "end_time": {
                            "type": "time",
                            "format": "HH:MM",
                            "required": True,
                        },
                        "no_of_hours": {"type": "number", "required": True},
                        "reason": {"type": "textarea", "required": True},
                        "remarks": {"type": "textarea", "required": True},
                    }
                },
            }
        },
    }

    if access_type == "respond":
        data["data"]["type"]["leave"]["data"]["employee_id"]["editable"] = False
        data["data"]["type"]["leave"]["data"]["leave_type"]["editable"] = False
        data["data"]["type"]["leave"]["data"]["reason"]["editable"] = False

        data["data"]["type"]["permission"]["data"]["employee_id"]["editable"] = False
        data["data"]["type"]["permission"]["data"]["leave_type"]["editable"] = False
        data["data"]["type"]["permission"]["data"]["reason"]["editable"] = False

        data["data"]["type"]["leave"]["actions"] = leave_respond_action
        data["data"]["type"]["permission"]["actions"] = permission_respond_action

    elif access_type == "request":
        data["data"]["type"]["leave"]["actions"] = leave_request_action
        data["data"]["type"]["permission"]["actions"] = permission_request_action
        data["data"]["type"]["leave"]["data"].pop("remarks")
        data["data"]["type"]["permission"]["data"].pop("remarks")

    elif access_type == "post":
        data["data"]["type"]["leave"]["actions"] = leave_post_action
        data["data"]["type"]["permission"]["actions"] = permission_post_action
        data["data"]["type"]["leave"]["data"].pop("remarks")
        data["data"]["type"]["permission"]["data"].pop("remarks")

    if type == "leave" and access_type == "respond":
        data["data"]["type"].pop("permission")

    elif type == "permission" and access_type == "respond":
        data["data"]["type"].pop("leave")

    return data


@router.post("/")
@role_required(["HR", "MD"])
async def post_leave(
    LeaveCreateRequest: LeaveCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
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
    status: StatusEnum = None,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    if status and status.value == "all":
        status = None
    leave_controller = LeaveController(payload, mongo_client)
    res = await leave_controller.get_leave_history(employee_id, status)
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
