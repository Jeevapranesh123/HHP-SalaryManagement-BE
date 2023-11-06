import sys

sys.dont_write_bytecode = True
from fastapi import FastAPI, Request, Response
from app.api import api_router
from app.core.errors import http_error_handler
from starlette.exceptions import HTTPException

from starlette.middleware.base import BaseHTTPMiddleware

from app.database import mongo

# from fastapi_jwt_auth import AuthJWT

# from app.core.config import Settings

app = FastAPI(
    title="HHP Salary Management APIs",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="0.0.1",
)


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


from fastapi import WebSocket, WebSocketDisconnect


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")


# @AuthJWT.load_config
# def get_config():
#     return Settings()


app.include_router(api_router, prefix="/api/v1")

app.add_exception_handler(HTTPException, http_error_handler)

# app.add_exception_handler(Response,)
