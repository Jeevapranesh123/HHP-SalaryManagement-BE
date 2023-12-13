from pydantic import BaseModel
from app.schemas.response import BaseResponse
import datetime
from bson import ObjectId
from pydantic.fields import Field
from enum import Enum


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponseDict(BaseModel):
    email: str
    access_token: str


class LoginResponse(BaseResponse):
    data: LoginResponseDict


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserBase(BaseModel):
    employee_id: str
    uuid: str
    email: str
    password: str
    primary_role: PyObjectId = Field(default_factory=PyObjectId, alias="primary_role")
    secondary_roles: list = []
    verified: bool = False
    is_active: bool = True
    created_by: str = None
    created_at: datetime.datetime = datetime.datetime.utcnow()
    changed_password_at_first_login: bool = False
    last_login: datetime.datetime = None
    last_password_change: datetime.datetime = None
    last_password_reset: datetime.datetime = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseResponse):
    # FIXME: Remove the token from the response all the end of development
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


class RoleTypes(str, Enum):
    primary = "primary"
    secondary = "secondary"


class AssignRoleReq(BaseModel):
    employee_id: str
    role: str
    type: RoleTypes


class RemoveRoleReq(BaseModel):
    employee_id: str
    role: str
    type: RoleTypes
