from pydantic import BaseModel, model_validator, root_validator
from typing import List, Optional
import datetime


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


class EmployeeBase(BaseModel):  # TODO: Add relevant fields in the future
    employee_id: str
    name: str
    email: str
    phone: str
    department: str
    designation: str
    bank_details: Optional[BankDetails] = None
    address: Optional[Address] = None
    govt_id_proofs: Optional[GovtIDProofs] = None
    # TODO: Father/Husband Phone Number (Optional) - decide on how to store this
