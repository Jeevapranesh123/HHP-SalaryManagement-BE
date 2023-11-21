from fastapi import HTTPException
from app.database import AsyncIOMotorClient

from app.api.crud import auth as auth_crud

from app.api.utils.employees import *

from app.api.utils.employees import verify_password


async def login(login_request, mongo_client: AsyncIOMotorClient):
    email = login_request.email
    password = login_request.password

    user = await auth_crud.check_if_email_exists(email, mongo_client)

    print(user)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    roles = await auth_crud.get_roles_with_id(user["roles"], mongo_client)

    for role in roles:
        print(role["role"])

    if not await verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    token = await create_access_token(
        data={
            "uuid": user["uuid"],
            "email": user["email"],
            "changed_password_at_first_login": user["changed_password_at_first_login"],
            "employee_id": user["employee_id"],
            "roles": [role["role"] for role in roles],
        },
        token_type="access",
        mongo_client=mongo_client,
    )

    return {"email": user["email"], "token": token}


async def logout():
    return {"message": "Hello World"}


async def change_password(
    email, change_password_request, mongo_client: AsyncIOMotorClient
):
    user = await auth_crud.get_user_with_email(email, mongo_client)

    if not user:
        raise HTTPException(status_code=400, detail="User with email does not exist")

    if not await verify_password(
        change_password_request.old_password, user["password"]
    ):
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    if change_password_request.new_password != change_password_request.confirm_password:
        raise HTTPException(
            status_code=400, detail="New password and confirm password do not match"
        )

    # FIXME: Check if new password is same as old password

    new_password = await hash_password(change_password_request.new_password)

    await auth_crud.update_password(user["email"], new_password, mongo_client)

    await auth_crud.change_password(user["email"], mongo_client)

    return {"message": "Password Changed Successfully"}


async def forgot_password(forgot_password_request, mongo_client: AsyncIOMotorClient):
    user = await auth_crud.get_user_with_email(
        forgot_password_request.email, mongo_client
    )

    if not user:
        raise HTTPException(status_code=400, detail="User with email does not exist")

    if not user["changed_password_at_first_login"]:
        raise HTTPException(
            status_code=400,
            detail="User account password has not been changed since creation",
        )

    token = await create_access_token(
        data={
            "uuid": user["uuid"],
            "email": user["email"],
        },
        token_type="reset-password",
        mongo_client=mongo_client,
    )

    # TODO: Send email with token to user
    return {"token": token}


async def reset_password(
    token_data, reset_password_request, mongo_client: AsyncIOMotorClient
):
    user = await auth_crud.get_user_with_email(token_data["email"], mongo_client)

    if not user:
        raise HTTPException(status_code=400, detail="User with email does not exist")

    if reset_password_request.new_password != reset_password_request.confirm_password:
        raise HTTPException(
            status_code=400, detail="New password and confirm password do not match"
        )

    new_password = await hash_password(reset_password_request.new_password)

    await auth_crud.update_password(user["email"], new_password, mongo_client)

    await auth_crud.delete_jwt_id(token_data["jti"], mongo_client)

    return {"message": "Password Reset Successful"}


async def get_logged_in_user(employee_id: str, mongo_client: AsyncIOMotorClient):
    return await auth_crud.get_logged_in_user(employee_id, mongo_client)


async def assign_role(role_req, mongo_client: AsyncIOMotorClient):
    employee = await auth_crud.get_user_with_employee_id(
        role_req.employee_id, mongo_client
    )

    if not employee:
        raise HTTPException(
            status_code=400,
            detail="Employee with employee_id {} does not exist".format(
                role_req.employee_id
            ),
        )

    role = await auth_crud.get_role(role_req.role, mongo_client)

    if not role:
        raise HTTPException(status_code=400, detail="Role does not exist")

    update = await auth_crud.assign_role(
        employee["employee_id"], role["_id"], mongo_client
    )

    if update:
        return True

    return False


async def remove_role(role_req, mongo_client: AsyncIOMotorClient):
    employee = await auth_crud.get_user_with_employee_id(
        role_req.employee_id, mongo_client
    )

    if not employee:
        raise HTTPException(
            status_code=400,
            detail="Employee does not exist".format(role_req.employee_id),
        )

    role = await auth_crud.get_role(role_req.role, mongo_client)

    if not role:
        raise HTTPException(status_code=400, detail="Role does not exist")

    update = await auth_crud.remove_role(
        employee["employee_id"], role["_id"], mongo_client
    )

    if update:
        return True

    return False
