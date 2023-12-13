import os
import orjson
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# from pydantic import BaseModel

load_dotenv(".env")


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST") or "localhost"
    RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME") or "root"
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD") or "zuvaLabs"

    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT") or "localhost:9000"
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY") or "minioadmin"
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY") or "minioadmin"

    MINIO_BUCKET = os.getenv("MINIO_BUCKET") or "salary-management"

    MONGO_HOST = os.getenv("MONGO_HOST") or "localhost"
    MONGO_PORT = os.getenv("MONGO_PORT") or 27017
    MONGO_DATABASE = os.getenv("MONGO_DATABASE") or "hhp-esm"
    MONGO_USERNAME = os.getenv("MONGO_USERNAME") or "root"
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD") or "root"

    MONGO_DATABASE = os.getenv("MONGO_DATABASE") or "hhp-esm"

    USERS_COLLECTION = os.getenv("USERS_COLLECTION") or "users"

    EMPLOYEE_COLLECTION = os.getenv("EMPLOYEES_COLLECTION") or "employees"

    SALARY_COLLECTION = os.getenv("SALARY_COLLECTION") or "salary"

    LEAVE_COLLECTION = os.getenv("LEAVE_COLLECTION") or "leave"

    LOAN_COLLECTION = os.getenv("LOAN_COLLECTION") or "loan"

    ROLES_COLLECTION = os.getenv("ROLES_COLLECTION") or "roles"

    TEMP_JWT_ID_COLLECTION = os.getenv("TEMP_JWT_ID_COLLECTION") or "jtis"

    ATTENDANCE_COLLECTION = os.getenv("ATTENDANCE_COLLECTION") or "attendance"

    LOCATION_COLLECTION = os.getenv("LOCATION_COLLECTION") or "location"

    LOAN_SCHEDULE_COLLECTION = os.getenv("LOAN_SCHEDULE_COLLECTION") or "loan_schedule"

    NOTIFICATION_COLLECTION = os.getenv("NOTIFICATION_COLLECTION") or "notifications"

    MONTHLY_COMPENSATION_COLLECTION = (
        os.getenv("MONTHLY_COMPENSATION_COLLECTION") or "monthly_compensation"
    )

    SALARY_INCENTIVES_COLLECTION = (
        os.getenv("SALARY_INCENTIVES_COLLECTION") or "salary_incentives"
    )

    SALARY_ADVANCE_COLLECTION = (
        os.getenv("SALARY_ADVANCE_COLLECTION") or "salary_advance"
    )

    OTHER_SALARY_COMPONENTS_COLLECTION = (
        os.getenv("OTHER_SALARY_COMPONENTS_COLLECTION") or "other_salary_components"
    )

    RULES_AND_GUIDELINES_COLLECTION = (
        os.getenv("RULES_AND_GUIDELINES_COLLECTION") or "rules_and_guidelines"
    )

    BRANCHES = ["HHP", "SAM"]

    BRANCH_DROPDOWN = [{"label": x, "value": x} for x in BRANCHES]


# class Settings(BaseModel):
#     authjwt_secret_key: str = "secret"


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content):
        return orjson.dumps(content)
