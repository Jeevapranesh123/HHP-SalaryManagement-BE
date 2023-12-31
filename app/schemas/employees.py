from pydantic import BaseModel, model_validator, root_validator, validator
from typing import List, Optional
from fastapi import HTTPException
from enum import Enum

from app.core.config import Config


class BankDetails(BaseModel):
    bank_name: str
    account_number: str
    ifsc_code: str
    branch: str
    address: str


class Address(BaseModel):
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    country: Optional[str] = "India"
    pincode: Optional[str] = None


class GovtIDProofs(BaseModel):
    aadhar: str
    pan: str
    voter_id: Optional[str] = None
    driving_license: Optional[str] = None
    passport: Optional[str] = None


# class BranchEnum(str, Enum):
#     HHP = "hhp"
#     SAM = "sam"

BranchEnum = Enum("BranchEnum", {branch: branch for branch in Config.BRANCHES})


class EmployeeBase(BaseModel):  # TODO: Add relevant fields in the future
    employee_id: str
    name: str
    email: str
    phone: str = "0000000000"
    branch: BranchEnum
    is_marketing_staff: Optional[bool] = False
    is_marketing_manager: Optional[bool] = False
    marketing_manager: Optional[str] = None
    profile_image_path: Optional[str] = None
    profile_image: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    bank_details: Optional[BankDetails]
    address: Optional[Address]
    govt_id_proofs: Optional[GovtIDProofs]
    # TODO: Father/Husband Phone Number (Optional) - decide on how to store this

    @validator("phone")
    def phone_validator(cls, v):
        if len(v) != 10:
            raise HTTPException(
                status_code=400, detail="Phone number must be 10 digits"
            )
        return v

    # FIXME: Add validation for aadhar, pan, voter_id, driving_license, passport
    # FIXME: Add validation for bank_name, account_number, ifsc_code, branch, address
    # FIXME: Add validation for email


from enum import Enum


class StatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    all = "all"
