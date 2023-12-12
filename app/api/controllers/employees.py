from fastapi import HTTPException, UploadFile, File

from app.database import AsyncIOMotorClient

from app.api.utils.employees import validate_new_employee, validate_update_employee

from app.api.crud import employees as employee_crud
from app.api.controllers.salary import SalaryController

from app.schemas.request import EmployeeCreateRequest, EmployeeUpdateRequest
from app.schemas.employees import EmployeeBase

from app.core.config import Config
from app.api.utils import *


from app.api.lib.RabbitMQ import RabbitMQ
from app.api.lib.MinIO import MinIO


from datetime import timedelta

import datetime


MONGO_DATABASE = Config.MONGO_DATABASE
LEAVE_COLLECTION = Config.LEAVE_COLLECTION
ATTENDANCE_COLLECTION = Config.ATTENDANCE_COLLECTION


async def get_file_size(file: UploadFile):
    # Seek to the end of the file to find its size
    await file.seek(0, 2)  # Seek to the end of the file
    file_size = file.tell()  # Get the file size

    # Seek back to the start of the file for future operations
    await file.seek(0)

    return file_size


class EmployeeController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.employee_id = payload["employee_id"]
        self.employee_role = payload["primary_role"]
        self.mongo_client = mongo_client

    async def upload_profile_image(self, employee_id, file: UploadFile = File(...)):
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=400, detail="Only JPEG and PNG images are allowed"
            )

        minio_client = MinIO()

        file_extension = file.content_type.split("/")[1]
        file_name = f"{employee_id}"
        object_name = f"profile/{file_name}"

        result = minio_client.client.put_object(
            minio_client.bucket_name,
            object_name,
            file.file,
            length=-1,
            content_type=file.content_type,
            part_size=15 * 1024 * 1024,
        )

        file_path = f"{minio_client.bucket_name}/{object_name}"

        file_path = "salary-management/profile/{}".format(file_name)

        return file_path

    async def set_branch(self, employee_id, branch):
        if not self.employee_role in ["MD"]:
            raise HTTPException(status_code=403, detail="Not Enough Permissions")
        emp = await employee_crud.get_employee(employee_id, self.mongo_client)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")

        emp["branch"] = branch

        await employee_crud.update_employee(employee_id, emp, self.mongo_client)

        return emp

    async def create_employee(self, employee: EmployeeCreateRequest):
        is_valid, message = await validate_new_employee(employee, self.mongo_client)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)

        emp_in_create = EmployeeBase(**employee.model_dump())

        # FIXME: Validate this logic of marketing staff and manager

        if emp_in_create.is_marketing_staff and not emp_in_create.is_marketing_manager:
            if not emp_in_create.marketing_manager:
                raise HTTPException(
                    status_code=400,
                    detail="Marketing Manager is required for Marketing Staff",
                )

            manager = await employee_crud.get_employee(
                emp_in_create.marketing_manager, self.mongo_client
            )

            if not manager:
                raise HTTPException(
                    status_code=400, detail="Marketing Manager not found"
                )

            if not manager["is_marketing_manager"]:
                raise HTTPException(
                    status_code=400,
                    detail="{} is not a Marketing Manager".format(
                        manager["employee_id"]
                    ),
                )

        elif emp_in_create.is_marketing_manager:
            emp_in_create.is_marketing_staff = True

            emp_in_create.marketing_manager = None

            # Add the MD id as marketing manager

        emp_in_create.profile_image_path = "profile/{}".format(
            emp_in_create.employee_id
        )

        emp, user = await employee_crud.create_employee(
            emp_in_create, self.employee_id, self.mongo_client
        )

        # sal_obj = SalaryController(self.payload, self.mongo_client)

        # await sal_obj.create_all_salaries(emp_in_create)

        mq = RabbitMQ()

        queue_name = "notifications_employee_{}".format(user.uuid)

        mq.ensure_queue(queue_name)
        mq.bind_queue(queue_name, "employee_notification", emp["employee_id"])

        # TODO: Push notification to MD regarding new employee creation

        return emp

    async def get_employee(self, employee_id: str):
        if not self.employee_role in ["HR", "MD"] and employee_id != self.employee_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        res, emp = await employee_crud.get_employee_with_computed_fields(
            employee_id, self.mongo_client
        )
        import pprint

        pprint.pprint(emp)
        is_marketing_staff = emp.get("is_marketing_staff", None)
        is_marketing_manager = emp.get("is_marketing_manager", None)

        if is_marketing_staff is not None:
            res["basic_information"]["is_marketing_staff"] = (
                "Yes" if emp["is_marketing_staff"] else "No"
            )

        if is_marketing_manager is not None:
            res["basic_information"]["is_marketing_manager"] = (
                "Yes" if emp["is_marketing_manager"] else "No"
            )

        res["basic_information"]["marketing_manager"] = emp["marketing_manager"]

        if self.employee_role == "HR" and self.employee_id == employee_id:
            pass
        elif self.employee_role == "HR":
            res["basic_salary"].pop("net_salary")
            res["basic_salary"].pop("gross_salary")
            res["monthly_compensation"].pop("other_special_allowance")
            res.pop("loan_and_advance")
            res.pop("salary_incentives")

        return res

    async def get_all_employees(self):
        branch = None
        requester = await employee_crud.get_employee(
            self.employee_id, self.mongo_client
        )
        branch = requester["branch"]
        # FIXME: Check with UI, how to implement this

        return await employee_crud.get_all_employees(branch, self.mongo_client)

    async def update_employee(
        self, employee_id, employee_details: EmployeeUpdateRequest
    ):
        emp_in_update = employee_details.model_dump()

        emp = await employee_crud.get_employee(employee_id, self.mongo_client)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")

        is_valid, message = await validate_update_employee(
            employee_id, employee_details, self.mongo_client
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        # FIXME: Update salary if needed
        minio = MinIO()

        profile_image_pre_signed_url = minio.client.presigned_get_object(
            Config.MINIO_BUCKET,
            emp["profile_image_path"],
            expires=timedelta(days=1),
        )

        emp_in_update["profile_image"] = profile_image_pre_signed_url

        emp = await employee_crud.update_employee(
            employee_id, emp_in_update, self.mongo_client
        )

        return emp

    async def get_editable_fields(self):
        return [
            {
                "basic_information": {
                    "name": True,
                    "phone": True,
                    "department": True,
                    "designation": True,
                    "branch": True,
                    # "profile_image": True,
                    "is_marketing_staff": True,
                    "is_marketing_manager": True,
                    "marketing_manager": True,
                }
            },
            {
                "bank_details": {
                    "bank_name": True,
                    "account_number": True,
                    "ifsc_code": True,
                    "branch": True,
                    "address": True,
                }
            },
            {
                "address": {
                    "address_line_1": True,
                    "address_line_2": True,
                    "city": True,
                    "state": True,
                    "country": True,
                    "pincode": True,
                }
            },
            {
                "govt_id_proofs": {
                    "aadhar": True,
                    "pan": True,
                    "voter_id": True,
                    "driving_license": True,
                    "passport": True,
                }
            },
        ]

    async def get_create_required_fields(self):
        return [
            {"employee_id": True},
            {"name": True},
            {"email": True},
            {"phone": True},
        ]
