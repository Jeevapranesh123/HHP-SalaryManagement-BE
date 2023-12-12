from app.database import get_mongo, AsyncIOMotorClient

from app.core.config import Config


MONGO_DATABASE = Config.MONGO_DATABASE
RULES_AND_GUIDELINES_COLLECTION = Config.RULES_AND_GUIDELINES_COLLECTION
ROLES_COLLECTION = Config.ROLES_COLLECTION


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
            upsert=True,
        )

        return rules

    async def post_guidelines(self, guidelines):
        guidelines = await self.mongo_client[MONGO_DATABASE][
            RULES_AND_GUIDELINES_COLLECTION
        ].update_one(
            {"id": "guidelines"},
            {"$set": guidelines},
            upsert=True,
        )

        return guidelines

    async def get_rules(self):
        rules = await self.mongo_client[MONGO_DATABASE][
            RULES_AND_GUIDELINES_COLLECTION
        ].find_one({"id": "rules"}, {"_id": 0})

        return rules

    async def get_guidelines(self):
        guidelines = await self.mongo_client[MONGO_DATABASE][
            RULES_AND_GUIDELINES_COLLECTION
        ].find_one({"id": "guidelines"}, {"_id": 0})

        return guidelines

    async def get_roles(self):
        roles = (
            await self.mongo_client[MONGO_DATABASE][ROLES_COLLECTION]
            .find({}, {"_id": 0})
            .to_list(length=None)
        )

        roles = [role["role"] for role in roles]

        return roles
