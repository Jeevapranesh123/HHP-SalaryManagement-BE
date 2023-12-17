from app.database import get_mongo, AsyncIOMotorClient

from app.api.crud.admin import AdminCrud

from fastapi import HTTPException, Depends, APIRouter

from app.schemas.admin import (
    Rules,
    Guidelines,
    ReportType,
    BankSalaryBatchCreateRequest,
    BankSalaryBatchInDB,
    BankSalaryBatch,
)

import pprint


class AdminController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.mongo_client = mongo_client
        self.employee_id = payload["employee_id"]
        self.primary_role = payload["primary_role"]

    async def post_rules(self, rules: Rules):
        crud_obj = AdminCrud(self.payload, self.mongo_client)
        rules = rules.model_dump()
        return await crud_obj.post_rules(rules)

    async def get_rules(self):
        crud_obj = AdminCrud(self.payload, self.mongo_client)

        return await crud_obj.get_rules()

    async def get_rules_meta(self):
        meta = {
            "rules": {
                "data": {
                    "total_leave": {
                        "type": "string",
                        "required": True,
                    },
                    "medical_leave": {
                        "type": "string",
                        "required": True,
                    },
                    "permission": {
                        "type": "string",
                        "required": True,
                    },
                    "loan": {
                        "type": "string",
                        "required": True,
                    },
                    "increment": {
                        "type": "string",
                        "required": True,
                    },
                },
                "actions": [
                    {
                        "label": "Update",
                        "type": "button",
                        "variant": "default",
                        "action": {"url": "/admin/rules", "method": "PUT"},
                    }
                ],
            }
        }

        return meta

    async def get_guidelines(self):
        crud_obj = AdminCrud(self.payload, self.mongo_client)

        return await crud_obj.get_guidelines()

    async def post_guidelines(self, guidelines: Guidelines):
        crud_obj = AdminCrud(self.payload, self.mongo_client)
        guidelines = guidelines.model_dump()
        pprint.pprint(guidelines)
        processed_guidelines = {"guidelines": []}
        for guideline in guidelines["guidelines"]:
            processed_guidelines["guidelines"].append(
                {"id": guideline["id"], "content": guideline["content"].strip().title()}
            )

        pprint.pprint(processed_guidelines)
        return await crud_obj.post_guidelines(processed_guidelines)

    async def get_roles(self):
        crud_obj = AdminCrud(self.payload, self.mongo_client)

        roles = await crud_obj.get_roles()
        return roles

    async def get_employee_role(self, employee_id):
        crud_obj = AdminCrud(self.payload, self.mongo_client)

        user = await crud_obj.get_employee_role(employee_id)

        role = user["primary_role"]["role"]

        return role

    async def get_report_meta(self, type=None):
        if not type:
            data = [
                {"label": "Salary", "value": "salary"},
                {"label": "Increment", "value": "increment"},
                {"label": "Bonus", "value": "bonus"},
                {"label": "Allowance", "value": "allowance"},
                {
                    "label": "Attendance Special Allowance",
                    "value": "attendance_special_allowance",
                },
                {
                    "label": "Other Special Allowance",
                    "value": "other_special_allowance",
                },
                {"label": "Leave", "value": "leave"},
                {"label": "All", "value": "all"},
            ]

        elif type != None:
            if type == "salary":
                data = {
                    "salary": {
                        "data": {
                            "employee_id": {"type": "string", "required": True},
                            "month": {
                                "type": "month",
                                "format": "YYYY-MM-DD",
                                "required": True,
                            },
                        },
                        "actions": [
                            {
                                "label": "Submit",
                                "type": "button",
                                "variant": "default",
                                "action": {
                                    "url": "/admin/report/download/salary",
                                    "method": "GET",
                                },
                            }
                        ],
                    }
                }

            elif type == "increment":
                data = {
                    "increment": {
                        "data": {
                            "start_year": {"type": "year", "required": True},
                            "end_year": {"type": "year", "required": True},
                        },
                        "actions": [
                            {
                                "label": "Submit",
                                "type": "button",
                                "variant": "default",
                                "action": {
                                    "url": "/admin/report/download/increment",
                                    "method": "GET",
                                },
                            }
                        ],
                    }
                }

            elif type == "bonus":
                data = {
                    "bonus": {
                        "data": {
                            "start_year": {"type": "year", "required": True},
                            "end_year": {"type": "year", "required": True},
                        },
                        "actions": [
                            {
                                "label": "Submit",
                                "type": "button",
                                "variant": "default",
                                "action": {
                                    "url": "/admin/report/download/bonus",
                                    "method": "GET",
                                },
                            }
                        ],
                    }
                }

            elif type == "allowance":
                data = {
                    "allowance": {
                        "data": {
                            "start_year": {"type": "year", "required": True},
                            "end_year": {"type": "year", "required": True},
                        },
                        "actions": [
                            {
                                "label": "Submit",
                                "type": "button",
                                "variant": "default",
                                "action": {
                                    "url": "/admin/report/download/allowance",
                                    "method": "GET",
                                },
                            }
                        ],
                    }
                }

            elif type == "attendance_special_allowance":
                data = {
                    "attendance_special_allowance": {
                        "data": {
                            "start_year": {"type": "year", "required": True},
                            "end_year": {"type": "year", "required": True},
                        },
                        "actions": [
                            {
                                "label": "Submit",
                                "type": "button",
                                "variant": "default",
                                "action": {
                                    "url": "/admin/report/download/attendance_special_allowance",
                                    "method": "GET",
                                },
                            }
                        ],
                    }
                }

            elif type == "other_special_allowance":
                data = {
                    "other_special_allowance": {
                        "data": {
                            "start_year": {"type": "year", "required": True},
                            "end_year": {"type": "year", "required": True},
                        },
                        "actions": [
                            {
                                "label": "Submit",
                                "type": "button",
                                "variant": "default",
                                "action": {
                                    "url": "/admin/report/download/other_special_allowance",
                                    "method": "GET",
                                },
                            }
                        ],
                    }
                }

            elif type == "leave":
                data = {
                    "leave": {
                        "data": {
                            "start_year": {"type": "year", "required": True},
                            "end_year": {"type": "year", "required": True},
                        },
                        "actions": [
                            {
                                "label": "Submit",
                                "type": "button",
                                "variant": "default",
                                "action": {
                                    "url": "/admin/report/download/leave",
                                    "method": "GET",
                                },
                            }
                        ],
                    }
                }

            elif type == "all":
                data = {
                    "all": {
                        "data": {
                            "start_year": {"type": "year", "required": True},
                            "end_year": {"type": "year", "required": True},
                        },
                        "actions": [
                            {
                                "label": "Submit",
                                "type": "button",
                                "variant": "default",
                                "action": {
                                    "url": "/admin/report/download/all",
                                    "method": "GET",
                                },
                            }
                        ],
                    }
                }

        return data

    async def create_bank_salary_batch(self, create_bank_salary_batch):
        crud_obj = AdminCrud(self.payload, self.mongo_client)

        bank_salary_batch_in_db = BankSalaryBatchInDB(**create_bank_salary_batch.dict())

        bank_salary_batch_in_db.employee_ids = [
            employee_id.strip() for employee_id in bank_salary_batch_in_db.employee_ids
        ]

        bank_salary_batch_in_db = bank_salary_batch_in_db.model_dump()

        res = await crud_obj.create_bank_salary_batch(bank_salary_batch_in_db)
        res["batch_id"] = res.pop("id")
        return res

    async def get_bank_salary_batch(self, batch_id):
        crud_obj = AdminCrud(self.payload, self.mongo_client)
        res = await crud_obj.get_bank_salary_batch(batch_id)
        res["batch_id"] = res.pop("id")

        return res

    async def get_bank_salary_batch_list(self):
        crud_obj = AdminCrud(self.payload, self.mongo_client)
        res = await crud_obj.get_bank_salary_batch_list()
        return res

    async def delete_bank_salary_batch(self, batch_id):
        crud_obj = AdminCrud(self.payload, self.mongo_client)
        res = await crud_obj.delete_bank_salary_batch(batch_id)
        return res

    async def update_bank_salary_batch(self, batch_id, update_bank_salary_batch):
        crud_obj = AdminCrud(self.payload, self.mongo_client)

        batch = await crud_obj.get_bank_salary_batch(batch_id)

        if not batch:
            raise HTTPException(status_code=404, detail="Bank salary batch not found")

        # bank_salary_batch_in_db = BankSalaryBatchInDB(**update_bank_salary_batch.dict())

        # bank_salary_batch_in_db.employee_ids = [
        #     employee_id.strip() for employee_id in bank_salary_batch_in_db.employee_ids
        # ]

        # bank_salary_batch_in_db = bank_salary_batch_in_db.model_dump()

        res = await crud_obj.update_bank_salary_batch(
            batch_id, update_bank_salary_batch.model_dump()
        )
        res["batch_id"] = res.pop("id")
        return res

    async def get_bank_salary_batch_list_all(self):
        crud_obj = AdminCrud(self.payload, self.mongo_client)
        res = await crud_obj.get_bank_salary_batch_list_all()
        return res
