from fastapi import APIRouter, Depends, Response, Request, HTTPException
from app.database import get_mongo, AsyncIOMotorClient


from app.schemas.admin import Rules

from app.api.controllers.admin import AdminController


from app.api.utils.employees import verify_login_token, verify_custom_master_token

router = APIRouter()


@router.put("/rules")
async def post_rules(
    rules: Rules,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.post_rules(rules)

    if res:
        return {"message": "Rules created successfully"}
