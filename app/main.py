import sys

sys.dont_write_bytecode = True
from fastapi import FastAPI, Request, Response
from app.api import api_router
from app.core.errors import http_error_handler
from starlette.exceptions import HTTPException

from starlette.middleware.base import BaseHTTPMiddleware

from app.database import mongo

from fastapi.middleware.cors import CORSMiddleware

from app.api.lib.RabbitMQ import RabbitMQ


import socketio

mq = RabbitMQ()

mq.ensure_exchange("employee_notification")

app = FastAPI(
    title="HHP Salary Management APIs",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="0.0.1",
)


# Create a Socket.IO server instance
sio = socketio.AsyncServer(async_mode="asgi")
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


# Event handler for new connections
@sio.event
async def connect(sid, environ):
    print("Connected", sid)

    # Event handler for disconnections


@sio.event
async def disconnect(sid):
    print("Disconnected", sid)


# @sio.event
# async def connect(sid, environ):
#     mq = RabbitMQ(
#         queue_name="salary",
#         exchange_name="salary",
#         binding_key="salary",
#     )

#     mq.ensure_exchange("salary")
#     mq.ensure_queue("salary")
#     mq.bind_queue("salary", "salary", "salary")

#     def callback(ch, method, properties, body):
#         print(" [x] %r:%r" % (method.routing_key, body))
#         sio.emit("notification", {"message": body.decode("utf-8")})

#     mq.consume("salary", callback)


# @sio.event
# async def disconnect(sid):
#     print("disconnect ", sid)


# app.mount("/", socket_app)


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
