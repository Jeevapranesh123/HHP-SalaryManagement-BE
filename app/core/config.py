import os
import orjson
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# from pydantic import BaseModel

load_dotenv(".env")


class Config(object):
    MONGO_HOST = os.getenv("MONGO_HOST") or "localhost"

    MONGO_PORT = os.getenv("MONGO_PORT") or 27017

    MONGO_DATABASE = os.getenv("MONGO_DATABASE") or "hhp-esm"

    MONGO_USERNAME = os.getenv("MONGO_USERNAME") or "root"

    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD") or "root"

    MONGO_DATABASE = os.getenv("MONGO_DATABASE") or "hhp-esm"

    USERS_COLLECTION = os.getenv("USERS_COLLECTION") or "users"

    EMPLOYEE_COLLECTION = os.getenv("EMPLOYEES_COLLECTION") or "employees"

    SALARY_COLLECTION = os.getenv("SALARY_COLLECTION") or "salary"

    TEMP_SALARY_COLLECTION = os.getenv("TEMP_SALARY_COLLECTION") or "temp_salary"

    LEAVE_COLLECTION = os.getenv("LEAVE_COLLECTION") or "leave"

    LOAN_COLLECTION = os.getenv("LOAN_COLLECTION") or "loan"

    ROLES_COLLECTION = os.getenv("ROLES_COLLECTION") or "roles"

    TEMP_JWT_ID_COLLECTION = os.getenv("TEMP_JWT_ID_COLLECTION") or "jtis"

    OTHER_SALARY_COMPONENTS_COLLECTION = (
        os.getenv("OTHER_SALARY_COMPONENTS_COLLECTION") or "other_salary_components"
    )


# class Settings(BaseModel):
#     authjwt_secret_key: str = "secret"


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content):
        return orjson.dumps(content)
