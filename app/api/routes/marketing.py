from fastapi import APIRouter, Depends, Response, Request

from app.database import get_mongo, AsyncIOMotorClient

from app.schemas.marketing import LocationEntry

from app.api.controllers.marketing import MarketingController

from app.api.utils.employees import verify_login_token

from fastapi import Query

import datetime
from datetime import date as date_class

router = APIRouter()


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


@router.get("/entries/daily")
async def get_daily_entries(
    date: datetime.date = Query(example=date_class.today().isoformat()),
    employee_id: str = None,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Get daily entries"""

    obj = MarketingController(payload, mongo_client)

    entries = await obj.get_daily_entries(employee_id, date)

    if entries:
        return {
            "message": "Entries retrieved successfully",
            "status_code": 200,
            "data": entries,
        }
