from app.schemas.employees import EmployeeBase
from app.schemas.request import EmployeeUpdateRequest
from app.database import AsyncIOMotorClient
from fastapi import HTTPException, Security, Header


from passlib.context import CryptContext

from app.core.config import Config
from datetime import datetime, timedelta
import string
import secrets

from app.api.crud import auth as auth_crud
import uuid
import jwt

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_mongo
from dotenv import load_dotenv
import os

load_dotenv()


MONGO_DATABASE = Config.MONGO_DATABASE
EMPLOYEE_COLLECTION = Config.EMPLOYEE_COLLECTION

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def check_if_employee_id_exists(employee_id, mongo_client: AsyncIOMotorClient):
    return await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].find_one(
        {"employee_id": employee_id}
    )


async def check_if_email_exists(email, mongo_client: AsyncIOMotorClient):
    return await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].find_one(
        {"email": email}
    )


async def check_if_phone_exists(phone, mongo_client: AsyncIOMotorClient):
    return await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].find_one(
        {"phone": phone}
    )


async def validate_new_employee(
    employee: EmployeeBase, mongo_client: AsyncIOMotorClient
):
    if await check_if_employee_id_exists(employee.employee_id, mongo_client):
        return False, "Employee ID already exists"
    if await check_if_email_exists(employee.email, mongo_client):
        return False, "Email already exists"
    if await check_if_phone_exists(employee.phone, mongo_client):
        return False, "Phone already exists"
    return True, "Validated"


async def validate_update_employee(
    employee_id,
    employee_details: EmployeeUpdateRequest,
    mongo_client: AsyncIOMotorClient,
):
    emp = await check_if_employee_id_exists(employee_id, mongo_client)
    if not emp:
        return False, "Employee ID does not exist"

    if not employee_details.phone == emp["phone"]:
        if await check_if_phone_exists(employee_details.phone, mongo_client):
            return False, "Phone already exists"

    return True, "Validated"


async def generate_random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for i in range(length))
    return password


async def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(
    data: dict, token_type, mongo_client, expires_delta: timedelta = None
):
    jti = await auth_crud.find_jwt_id(data["uuid"], token_type, mongo_client)
    if jti:
        await auth_crud.delete_jwt_id(jti["jwt_id"], mongo_client)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    id = str(uuid.uuid4()).replace("-", "")

    to_encode.update({"jti": id})
    to_encode.update({"type": token_type})
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    await auth_crud.store_jwt_id(id, data["uuid"], token_type, mongo_client)

    return encoded_jwt


# Dependency for getting the JWT token from the Authorization header
security = HTTPBearer()


async def verify_login_token(
    http_auth_credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    token = http_auth_credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid authentication")

        if payload.get("exp") < int(datetime.utcnow().timestamp()):
            raise HTTPException(status_code=401, detail="Token has expired")

        mongo_client = await get_mongo()

        user = await auth_crud.get_user_by_uuid(payload["uuid"], mongo_client)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        return payload  # or any specific user data you need from the payload
    except jwt.PyJWTError as e:
        print(e)
        raise HTTPException(status_code=403, detail="Could not validate credentials")


async def verify_tokens(token: str, token_type: str, mongo_client: AsyncIOMotorClient):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if not await auth_crud.check_jwt_id(payload["jti"], mongo_client):
            raise HTTPException(status_code=401, detail="Token already used or invalid")

        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        if payload.get("exp") < int(datetime.utcnow().timestamp()):
            raise HTTPException(status_code=401, detail="Token has expired")

        # await auth_crud.delete_jwt_id(payload["jti"], mongo_client)

        return payload  # or any specific user data you need from the payload
    except jwt.PyJWTError as e:
        print(e)
        raise HTTPException(status_code=403, detail="Could not validate credentials")


async def verify_custom_master_token(
    http_auth_credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    token = http_auth_credentials.credentials
    try:
        if token == os.getenv("CREATE_EMPLOYEE_TOKEN"):
            return {
                "uuid": "abc123",
                "email": "jeevadev02@gmail.com",
                "changed_password_at_first_login": True,
                "employee_id": "MASTER1001",
                "primary_role": "MD",
                "secondary_roles": ["employee"],
                "type": "master",
            }
        else:
            return await verify_login_token(http_auth_credentials)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail="Could not validate credentials")
