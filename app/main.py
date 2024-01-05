import sys

sys.dont_write_bytecode = True
import os
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

from sentry_sdk.crons import monitor

import sentry_sdk

from dotenv import load_dotenv
from pytz import timezone

import datetime


import logging

# logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

# logger = logging.getLogger(__name__)

import random

import string

import time

load_dotenv()

try:
    mq = RabbitMQ()

    mq.ensure_exchange("employee_notification")

    mq.connection.close()
except Exception as e:
    print(e)

if os.getenv("ENVIRONMENT") == "prod" or os.getenv("ENVIRONMENT") == "staging":
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        enable_tracing=True,
    )

app = FastAPI(
    title="HHP Salary Management APIs",
    description="This is the API documentation for the HHP Salary Management System",
    version="0.0.1",
)


# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
#     logger.info(f"rid={idem} start request path={request.url.path}")
#     start_time = time.time()

#     response = await call_next(request)

#     process_time = (time.time() - start_time) * 1000
#     formatted_process_time = "{0:.2f}".format(process_time)
#     logger.info(
#         f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}"
#     )

#     return response


local_tz = timezone("Asia/Kolkata")

scheduler = AsyncIOScheduler(timezone=local_tz)


# @monitor(monitor_slug="attendance-job")
async def attendance_job():
    with monitor(monitor_slug="attendance-marking-job"):
        obj = Attendance(mongo.client)
        list = await obj.post_attendance()
        print("Attendance Job Ran", datetime.datetime.now())


async def salary_job():
    with monitor(monitor_slug="salary-increment-job"):
        obj = SalaryCron(mongo.client)
        await obj.update_basic_salary()
        print("Salary Job Ran")


scheduler.add_job(salary_job, "cron", day="last", hour=23, minute=00, second=00)


scheduler.add_job(attendance_job, "cron", hour=18, minute=00, second=00)

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


@app.on_event("shutdown")
async def shutdown():
    await mongo.close_database_connection()


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/attendance")
async def test():
    # obj = Attendance(mongo.client)
    # await obj.post_attendance()
    await attendance_job()


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
