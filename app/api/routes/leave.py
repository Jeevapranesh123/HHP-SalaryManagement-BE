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


@router.get("/meta")
async def get_meta(
    access_type: str,
    type: str = None,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
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
                    "actions": [
                        {
                            "label": "Approve",
                            "type": "button",
                            "color": "green",
                            "action": {"url": "/leave/respond", "method": "POST"},
                        },
                        {
                            "label": "Reject",
                            "type": "button",
                            "color": "red",
                            "action": {"url": "/leave/respond", "method": "POST"},
                        },
                    ],
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
                    },
                    "meta": {"url": "/permission/", "method": "POST"},
                },
            }
        },
    }

    if type == "leave":
        data["data"]["type"].pop("permission")

    elif type == "permission":
        data["data"]["type"].pop("leave")

    if access_type == "respond":
        data["data"]["type"]["leave"]["data"]["employee_id"]["editable"] = False
        data["data"]["type"]["leave"]["data"]["leave_type"]["editable"] = False
        data["data"]["type"]["leave"]["data"]["reason"]["editable"] = False

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
    status: str = None,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
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
