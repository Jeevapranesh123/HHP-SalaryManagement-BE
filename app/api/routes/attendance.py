from fastapi import APIRouter, Depends, Response, Request

from app.database import get_mongo, AsyncIOMotorClient

from app.api.controllers.attendance import AttendanceController
