from app.core.config import Config
from app.database import AsyncIOMotorClient
import pprint
from app.api.utils import *
import uuid

from app.schemas.salary import SalaryBase
from app.schemas.db import SalaryInDB

MONGO_DATABASE = Config.MONGO_DATABASE
EMPLOYEE_COLLECTION = Config.EMPLOYEE_COLLECTION
SALARY_COLLECTION = Config.SALARY_COLLECTION
MONTHLY_COMPENSATION_COLLECTION = Config.MONTHLY_COMPENSATION_COLLECTION
SALARY_INCENTIVES_COLLECTION = Config.SALARY_INCENTIVES_COLLECTION


class SalaryCron:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.mongo_client = mongo_client

    async def build_new_salary(self, current_salary, incentives):
        new_gross = current_salary["gross_salary"] + incentives["increment"]

        new_salary = SalaryBase(
            employee_id=current_salary["employee_id"],
            gross_salary=new_gross,
            esi=current_salary["esi"],
            pf=current_salary["pf"],
        )

        new_month, new_year = get_next_month(
            current_salary["month"].month, current_salary["month"].year
        )
        new_month_date = datetime.datetime(new_year, new_month, 1)

        new_salary_in_db = SalaryInDB(
            **new_salary.model_dump(),
            month=new_month_date,
            created_by=current_salary["created_by"]
        )

        return new_salary_in_db.model_dump()

    async def update_basic_salary(self):
        employee_list = (
            await self.mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION]
            .find({})
            .to_list(length=None)
        )

        for emp in employee_list:
            employee_id = emp["employee_id"]

            # month = first_day_of_current_month()
            month = first_day_of_last_month()

            basic_salary = await self.mongo_client[MONGO_DATABASE][
                SALARY_COLLECTION
            ].find_one({"employee_id": employee_id, "month": month}, {"_id": 0})

            if basic_salary is None:
                basic_salary = SalaryBase(
                    employee_id=employee_id, gross_salary=0, esi=0, pf=0
                )

                basic_salary_in_db = SalaryInDB(
                    **basic_salary.model_dump(), month=month, created_by="Cron"
                )

                basic_salary = basic_salary_in_db.model_dump()

            incentives = await self.mongo_client[MONGO_DATABASE][
                SALARY_INCENTIVES_COLLECTION
            ].find_one(
                {"employee_id": employee_id, "month": basic_salary["month"]},
                {"_id": 0},
            )

            if incentives is None:
                incentives = {"increment": 0}

            new_salary = await self.build_new_salary(basic_salary, incentives)

            await self.mongo_client[MONGO_DATABASE][
                SALARY_COLLECTION
            ].find_one_and_replace(
                {"employee_id": employee_id, "month": new_salary["month"]},
                new_salary,
                upsert=True,
            )
