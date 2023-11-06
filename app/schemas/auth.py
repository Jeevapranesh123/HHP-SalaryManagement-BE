from pydantic import BaseModel
from app.schemas.response import BaseResponse
import datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseResponse):
    email: str
    access_token: str


class UserBase(BaseModel):
    employee_id: str
    uuid: str
    email: str
    password: str
    verified: bool = False
    is_active: bool = True
    created_by: str = None
    created_at: datetime.datetime = datetime.datetime.utcnow()
    changed_password_at_first_login: bool = False
    last_login: datetime.datetime = None
    last_password_change: datetime.datetime = None
    last_password_reset: datetime.datetime = None


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseResponse):
    # FIXME: Remove the token from the response all the end of development
    token: str
    message: str = "Email with reset token sent to user's email address"


class ResetPasswordRequest(BaseModel):
    new_password: str
    confirm_password: str


class ResetPasswordResponse(BaseResponse):
    message: str = "Password reset successful"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
