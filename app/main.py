import sys

sys.dont_write_bytecode = True
from fastapi import FastAPI, Request, Response
from app.api import api_router
from app.core.errors import http_error_handler
from starlette.exceptions import HTTPException

from starlette.middleware.base import BaseHTTPMiddleware

from app.database import mongo

from fastapi.middleware.cors import CORSMiddleware
import json
import pika
import threading
import socketio


class SocketIOManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi")
        self.app = socketio.ASGIApp(self.sio)

    async def on_connect(self, sid, environ):
        print("Client connected", sid)
        while True:
            await self.sio.sleep(1)
            await self.sio.emit("notification", {"message": "Hello"}, to=sid)
        # Perform authentication and other checks here
        # user = self.authenticate_user(environ)
        # if user:
        #     await self.setup_rabbitmq_consumer(sid, user)

    async def on_disconnect(self, sid):
        print("Client disconnected", sid)
        # Cleanup, e.g., stop RabbitMQ consumer thread

    # async def authenticate_user(self, environ):
    #     # Implement user authentication logic
    #     # Return user object if authenticated
    #     pass

    # async def setup_rabbitmq_consumer(self, sid, user):
    #     thread = threading.Thread(target=self.start_rabbitmq_consumer, args=(sid, user))
    #     thread.start()

    # def start_rabbitmq_consumer(self, sid, user):
    #     def callback(ch, method, properties, body):
    #         async_to_sync(self.sio.emit)('notification', {'message': body.decode()}, to=sid)


app = FastAPI(
    title="HHP Salary Management APIs",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="0.0.1",
)

# sio = socketio.AsyncServer(async_mode="asgi")
# socket_app = socketio.ASGIApp(sio)

# # Mount the Socket.IO application
# app.mount("/socket", socket_app)


# # Socket.IO events
# @sio.event
# async def connect(sid, environ):
#     print("Client connected", sid)
#     # while True:
#     #     await sio.sleep(1)
#     #     await sio.emit('notification', {'message': 'Hello'}, to=sid)


# @sio.event
# async def disconnect(sid):
#     print("Client disconnected", sid)


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
