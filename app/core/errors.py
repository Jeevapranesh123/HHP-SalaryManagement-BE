from starlette.responses import JSONResponse
from fastapi import Request
from starlette.exceptions import HTTPException


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        {"status": False, "message": [exc.detail]}, status_code=exc.status_code
    )
