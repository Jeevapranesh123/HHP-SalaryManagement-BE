from fastapi import APIRouter, Depends, Response, Request

from app.database import get_mongo, AsyncIOMotorClient

from app.api.controllers.attendance import AttendanceController

from app.api.utils.employees import verify_login_token, verify_custom_master_token

router = APIRouter()


@router.get("/{employee_id}")
async def get_attendance(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    att_obj = AttendanceController(employee_id, mongo_client)
    res = await att_obj.get_attendance()
    return {
        "message": "Attendance fetched successfully",
        "status_code": 200,
        "data": res,
    }
