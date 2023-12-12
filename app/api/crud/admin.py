from app.database import get_mongo, AsyncIOMotorClient

from app.core.config import Config


MONGO_DATABASE = Config.MONGO_DATABASE
RULES_AND_GUIDELINES_COLLECTION = Config.RULES_AND_GUIDELINES_COLLECTION


class AdminCrud:
    def __init__(self, payload, mongo_client: AsyncIOMotorClient):
        self.payload = payload
        self.mongo_client = mongo_client
        self.employee_id = payload["employee_id"]
        self.primary_role = payload["primary_role"]

    async def post_rules(self, rules):
        rules = await self.mongo_client[MONGO_DATABASE][
            RULES_AND_GUIDELINES_COLLECTION
        ].update_one(
            {"id": "rules"},
            {"$set": rules},
        )

        return rules
