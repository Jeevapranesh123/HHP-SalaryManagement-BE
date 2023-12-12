from fastapi import APIRouter, Depends, Response, Request, HTTPException

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    ChangePasswordRequest,
)

from app.database import get_mongo, AsyncIOMotorClient

from app.api.utils.employees import (
    verify_login_token,
    verify_tokens,
)
from app.api.controllers import auth as auth_controller

from app.api.utils.employees import verify_login_token


router = APIRouter()


@router.post("/login")
async def login(
    login_request: LoginRequest,
    response: Response,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await auth_controller.login(login_request, mongo_client)

    data = {"email": res["email"], "access_token": res["token"]}

    return LoginResponse(
        message="Login Successful",
        status_code=200,
        data=data,
    )


@router.get("/verify")
def verify_access_token(payload: dict = Depends(verify_login_token)):
    return {
        "message": "Token is valid",
        "status_code": 201,
        "data": payload,
    }


@router.post("/forgot-password")
async def forgot_password(
    forgot_password_request: ForgotPasswordRequest,
    response: Response,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await auth_controller.forgot_password(forgot_password_request, mongo_client)

    return ForgotPasswordResponse(
        status_code=200,
        token=res["token"],
    )


@router.post("/reset-password")
async def reset_password(
    token: str,
    reset_password_request: ResetPasswordRequest,
    response: Response,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    user = await verify_tokens(token, "reset-password", mongo_client)

    res = await auth_controller.reset_password(
        user, reset_password_request, mongo_client
    )

    return ResetPasswordResponse(
        status_code=200,
    )


@router.post("/change-password")
async def change_password(
    change_password_request: ChangePasswordRequest,
    response: Response,
    verfiy_login_token: dict = Depends(verify_login_token),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await auth_controller.change_password(
        verfiy_login_token["email"], change_password_request, mongo_client
    )

    return res


@router.post("/logout")
async def logout(
    response: Response,
):
    # FIXME: Find the cookie name and delete it
    response.delete_cookie("Authorization")

    return {"message": "Logout Successful"}


# FIXME: Use same controller for both this and get_employee
@router.get("/me")
async def get_logged_in_user(
    token: dict = Depends(verify_login_token),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
):
    res = await auth_controller.get_logged_in_user(token["employee_id"], mongo_client)

    return {
        "message": "Success",
        "status_code": 200,
        "data": res,
    }
