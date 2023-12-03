from app.database import get_mongo, AsyncIOMotorClient

from app.api.crud.admin import AdminCrud


class AdminController:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.mongo_client = mongo_client
        self.employee_id = payload["employee_id"]
        self.primary_role = payload["primary_role"]

    async def post_rules(self, rules):
        crud_obj = AdminCrud(self.payload, self.mongo_client)

        return await crud_obj.post_rules(rules)
