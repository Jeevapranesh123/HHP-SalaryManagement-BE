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
                        },
                        "leave_type": {
                            "type": "dropdown",
                            "options": [
                                {"label": "Casual", "value": "casual"},
                                {"label": "Medical", "value": "medical"},
                            ],
                        },
                        "start_date": {"type": "date", "format": "YYYY-MM-DD"},
                        "end_date": {"type": "date", "format": "YYYY-MM-DD"},
                        "no_of_days": {"type": "number"},
                        "reason": {"type": "textarea"},
                        "remarks": {"type": "textarea"},
                    },
                    "meta": {"url": "/leave/", "method": "POST"},
                },
                "permission": {
                    "data": {
                        "employee_id": {
                            "type": "string",
                        },
                        "leave_type": {
                            "type": "dropdown",
                            "options": [
                                {"label": "Permission", "value": "permission"},
                            ],
                        },
                        "date": {"type": "date", "format": "YYYY-MM-DD"},
                        "start_time": {"type": "time", "format": "HH:MM"},
                        "end_time": {"type": "time", "format": "HH:MM"},
                        "no_of_hours": {"type": "number"},
                        "reason": {"type": "textarea"},
                        "remarks": {"type": "textarea"},
                    },
                    "meta": {"url": "/permission/", "method": "POST"},
                },
            }
        },
    }

    if access_type == "request":
        data["data"]["type"]["leave"]["meta"]["url"] = "/leave/request"
        data["data"]["type"]["permission"]["meta"]["url"] = "/permission/request"
        data["data"]["type"]["leave"]["data"].pop("remarks")
        data["data"]["type"]["permission"]["data"].pop("remarks")

    elif access_type == "post":
        data["data"]["type"]["leave"]["meta"]["url"] = "/leave"
        data["data"]["type"]["permission"]["meta"]["url"] = "/permission"
        data["data"]["type"]["leave"]["data"].pop("reason")
        data["data"]["type"]["permission"]["data"].pop("reason")

    elif access_type == "respond":
        data["data"]["type"]["leave"]["meta"]["url"] = "/leave/respond"
        data["data"]["type"]["permission"]["meta"]["url"] = "/permission/respond"

    return data


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
