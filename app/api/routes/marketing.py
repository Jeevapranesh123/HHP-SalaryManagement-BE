from fastapi import APIRouter, Depends, Response, Request

from app.database import get_mongo, AsyncIOMotorClient

from app.schemas.marketing import LocationEntry

from app.api.controllers.marketing import MarketingController

from app.api.utils.employees import verify_login_token

from fastapi import Query

import datetime
from datetime import date as date_class

router = APIRouter()


@router.get("/entry/meta")
async def get_entry_meta(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Get entry meta data"""

    obj = MarketingController(payload, mongo_client)

    res = await obj.get_entry_meta()

    return {
        "message": "Entry meta data retrieved successfully",
        "status_code": 200,
        "data": res,
    }


@router.post("/entry", status_code=201)
async def post_entry(
    response: Response,
    entry: LocationEntry,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = MarketingController(payload, mongo_client)
    res = await obj.post_entry(entry)

    if res:
        response.status_code = 201
        return {"message": "Entry created successfully"}


@router.get("/entry/{entry_id}")
async def get_location_entry(
    entry_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Get daily entries"""

    obj = MarketingController(payload, mongo_client)

    entries = await obj.get_location_entry(entry_id)

    return {
        "message": "Entries retrieved successfully",
        "status_code": 200,
        "data": entries,
    }


@router.get("/employees")
async def get_employees(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Get employees"""

    obj = MarketingController(payload, mongo_client)

    employees = await obj.get_employees()

    return {
        "message": "Employees retrieved successfully",
        "status_code": 200,
        "data": employees,
    }


@router.get("/entries/{employee_id}")
async def get_daily_entries(
    employee_id: str,
    date: date_class = Query(None),
    start_date: date_class = Query(None),
    end_date: date_class = Query(None),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Get daily entries"""

    obj = MarketingController(payload, mongo_client)

    entries = await obj.get_entries(
        employee_id, date=date, start_date=start_date, end_date=end_date
    )

    return {
        "message": "Entries retrieved successfully",
        "status_code": 200,
        "data": entries,
    }
