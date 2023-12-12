import sys

sys.dont_write_bytecode = True
from fastapi import FastAPI, Request, Response, Depends
from app.api import api_router
from app.core.errors import http_error_handler
from starlette.exceptions import HTTPException

from starlette.middleware.base import BaseHTTPMiddleware

from app.database import mongo, AsyncIOMotorClient, get_mongo

from fastapi.middleware.cors import CORSMiddleware

from app.api.lib.RabbitMQ import RabbitMQ

from app.api.lib.Attendance import Attendance
from app.api.crons.salary import SalaryCron

from apscheduler.schedulers.asyncio import AsyncIOScheduler


mq = RabbitMQ()

mq.ensure_exchange("employee_notification")

mq.connection.close()

app = FastAPI(
    title="HHP Salary Management APIs",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="0.0.1",
)

scheduler = AsyncIOScheduler()


async def attendance_job():
    obj = Attendance(mongo.client)
    list = await obj.post_attendance()


async def salary_job():
    obj = SalaryCron(mongo.client)
    await obj.update_basic_salary()
    print("Salary Job Ran")


scheduler.add_job(salary_job, "cron", hour=14, minute=52, second=0)


# scheduler.add_job(attendance_job, "cron", minute="*/2")

scheduler.start()


class StatusCodeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if hasattr(request.state, "status_code"):
            response.status_code = request.state.status_code
        return response


app.add_middleware(StatusCodeMiddleware)


@app.on_event("startup")
async def startup():
    await mongo.connect_to_database()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/attendance")
async def test():
    obj = Attendance(mongo.client)
    await obj.post_attendance()


@app.get("/increment")
async def inc(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    obj = SalaryCron(mongo_client)
    await obj.update_basic_salary()


app.include_router(api_router, prefix="/api/v1")

app.add_exception_handler(HTTPException, http_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.add_exception_handler(Response,)

# FIXME: LOAN_SCHEDULE_INDEX = employee_id + loan_id + month
# FIXME: Add increment to next month gross salary

# TODO: Loan Repayment adjustment to next month
# TODO: Admin APIs for rules and complete monitoring
# FIXME: When a salary entry already exists, update it instead of creating a new one
# FIXME: When a role is removed for MD or HR, assign them the basic role of Employee
# FIXME: When sending notification, build the notificationBase such that multiple notifiers can get different notifications for the same event
# FIXME: When MD is assigned a role of MD, he is getting the notification twice


# Leave

# FIXME: When leave for same date is requested, return error


# FIXME: THE JWT Secret should be stored in a .env file, it currently in the crud file


# Loan

# FIXME: Run a cron every month to update the status of loan repayment schedule
