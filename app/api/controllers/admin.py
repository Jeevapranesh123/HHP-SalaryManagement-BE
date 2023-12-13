from app.database import get_mongo, AsyncIOMotorClient

from app.api.crud.admin import AdminCrud

from app.schemas.admin import Rules, Guidelines


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
        return await crud_obj.post_guidelines(guidelines)

    async def get_roles(self):
        crud_obj = AdminCrud(self.payload, self.mongo_client)

        roles = await crud_obj.get_roles()
        return roles

    async def get_employee_role(self, employee_id):
        crud_obj = AdminCrud(self.payload, self.mongo_client)

        user = await crud_obj.get_employee_role(employee_id)

        role = user["primary_role"]["role"]

        return role
