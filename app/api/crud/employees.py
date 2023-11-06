from app.schemas.employees import EmployeeBase
from app.schemas.db import EmployeeInDB
from app.database import AsyncIOMotorClient
from app.core.config import Config
from app.api.utils.employees import generate_random_password, hash_password
from app.schemas.auth import UserBase
import uuid


MONGO_DATABASE = Config.MONGO_DATABASE
EMPLOYEE_COLLECTION = Config.EMPLOYEE_COLLECTION
USERS_COLLECTION = Config.USERS_COLLECTION


async def create_employee(employee: EmployeeBase, mongo_client: AsyncIOMotorClient):
    employee = employee.model_dump()

    employee["uuid"] = str(uuid.uuid4()).replace("-", "")

    # password = generate_random_password()

    password = "string"
    employee["password"] = hash_password(password)

    print(password)

    await create_user(employee, mongo_client)

    # TODO: Send email with password to employee and insist on changing it on first login

    emp_in_db = EmployeeInDB(**employee)

    if await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].insert_one(
        emp_in_db.model_dump()
    ):
        return emp_in_db


async def create_user(employee: dict, mongo_client: AsyncIOMotorClient):
    user = UserBase(
        employee_id=employee["employee_id"],
        uuid=employee["uuid"],
        email=employee["email"],
        password=employee["password"],
    )

    if await mongo_client[MONGO_DATABASE][USERS_COLLECTION].insert_one(
        user.model_dump()
    ):
        return user

    return None
