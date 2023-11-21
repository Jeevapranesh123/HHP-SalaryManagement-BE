from app.database import AsyncIOMotorClient

from app.core.config import Config

MONGO_DATABASE = Config.MONGO_DATABASE
USERS_COLLECTION = Config.USERS_COLLECTION
EMPLOYEE_COLLECTION = Config.EMPLOYEE_COLLECTION
ROLES_COLLECTION = Config.ROLES_COLLECTION
TEMP_JWT_ID_COLLECTION = Config.TEMP_JWT_ID_COLLECTION
import datetime


async def check_if_email_exists(email, mongo):
    user = await mongo[MONGO_DATABASE][USERS_COLLECTION].find_one({"email": email})
    if user:
        return user
    return False


async def get_user_with_email(email, mongo: AsyncIOMotorClient):
    user = await mongo[MONGO_DATABASE][USERS_COLLECTION].find_one({"email": email})
    if user:
        return user
    return False


async def get_user_with_employee_id(employee_id, mongo: AsyncIOMotorClient):
    user = await mongo[MONGO_DATABASE][USERS_COLLECTION].find_one(
        {"employee_id": employee_id}
    )
    if user:
        return user
    return False


async def update_password(email, password, mongo: AsyncIOMotorClient):
    user = await mongo[MONGO_DATABASE][USERS_COLLECTION].update_one(
        {"email": email}, {"$set": {"password": password}}
    )
    if user:
        return user
    return False


async def store_jwt_id(id, uuid, type, mongo_client):
    await mongo_client[MONGO_DATABASE][TEMP_JWT_ID_COLLECTION].insert_one(
        {"jwt_id": id, "uuid": uuid, "type": type}
    )


async def check_jwt_id(id, mongo_client):
    return await mongo_client[MONGO_DATABASE][TEMP_JWT_ID_COLLECTION].find_one(
        {"jwt_id": id}
    )


async def find_jwt_id(uuid, type, mongo_client):
    return await mongo_client[MONGO_DATABASE][TEMP_JWT_ID_COLLECTION].find_one(
        {"uuid": uuid, "type": type}
    )


async def delete_jwt_id(id, mongo_client):
    return await mongo_client[MONGO_DATABASE][TEMP_JWT_ID_COLLECTION].delete_one(
        {"jwt_id": id}
    )


async def change_password(email, mongo_client):
    return await mongo_client[MONGO_DATABASE][USERS_COLLECTION].update_one(
        {"email": email},
        {
            "$set": {
                "changed_password_at_first_login": True,
                "last_password_change": datetime.datetime.utcnow(),
            }
        },
    )


async def get_logged_in_user(employee_id: str, mongo_client: AsyncIOMotorClient):
    emp = await mongo_client[MONGO_DATABASE][EMPLOYEE_COLLECTION].find_one(
        {"employee_id": employee_id}, {"_id": 0}
    )

    return emp


async def get_role(role, mongo_client):
    role = await mongo_client[MONGO_DATABASE][ROLES_COLLECTION].find_one({"role": role})

    return role


async def get_roles_with_id(roles, mongo_client):
    roles = mongo_client[MONGO_DATABASE][ROLES_COLLECTION].find({"_id": {"$in": roles}})
    return [x async for x in roles]


async def assign_role(employee_id, role_id, mongo_client):
    update = await mongo_client[MONGO_DATABASE][USERS_COLLECTION].update_one(
        {"employee_id": employee_id},
        {"$addToSet": {"roles": role_id}},
    )

    print(update.matched_count)

    return update


async def remove_role(employee_id, role_id, mongo_client):
    remove = await mongo_client[MONGO_DATABASE][USERS_COLLECTION].update_one(
        {"employee_id": employee_id},
        {"$pull": {"roles": role_id}},
    )

    return remove
