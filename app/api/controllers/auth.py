from fastapi import HTTPException
from app.database import AsyncIOMotorClient

from app.api.crud import auth as auth_crud
from app.api.crud import employees as employee_crud

from app.api.utils.employees import *

from app.api.utils.employees import verify_password
from app.schemas.salary import SalaryBase, MonthlyCompensationBase, SalaryIncentivesBase
from app.api.utils import *

from app.api.lib.MinIO import MinIO

from app.api.lib.RabbitMQ import RabbitMQ

from app.api.lib.Notification import Notification
from app.schemas.notification import (
    NotificationBase,
    SendNotification,
    NotificationMeta,
)
import pprint


LEAVE_COLLECTION = Config.LEAVE_COLLECTION


async def login(login_request, mongo_client: AsyncIOMotorClient):
    email = login_request.email
    password = login_request.password

    user = await auth_crud.check_if_email_exists(email, mongo_client)
    if not user:
        raise HTTPException(status_code=401, detail="User with email does not exist")

    if not await verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    primary_role = None
    secondary_roles = []

    if user["primary_role"]:
        primary_role = await auth_crud.get_role_with_id(
            user["primary_role"], mongo_client
        )
        primary_role = primary_role["role"]

    if user["secondary_roles"]:
        secondary_roles = await auth_crud.get_roles_with_id(
            user["secondary_roles"], mongo_client
        )
        secondary_roles = [role["role"] for role in secondary_roles]

    token = await create_access_token(
        data={
            "uuid": user["uuid"],
            "email": user["email"],
            "branch": user["info"]["branch"],
            "changed_password_at_first_login": user["changed_password_at_first_login"],
            "employee_id": user["employee_id"],
            "primary_role": primary_role,
            "secondary_roles": secondary_roles,
            "employee_name": user["info"]["name"],
        },
        token_type="access",
        mongo_client=mongo_client,
    )

    bind_key = []

    if primary_role and primary_role != "employee":
        bind_key.append(primary_role)

    bind_key.append(user["employee_id"])

    mq = RabbitMQ()
    mq.ensure_queue("notifications_employee_{}".format(user["uuid"]))
    for key in bind_key:
        if key == "HR":
            key = "HR_{}".format(user["info"]["branch"].replace(" ", "_"))
        mq.bind_queue(
            "notifications_employee_{}".format(user["uuid"]),
            "employee_notification",
            key,
        )

    # Update profile pre-signed url

    minio = MinIO()

    try:
        object = minio.client.stat_object(
            Config.MINIO_BUCKET, user["info"]["profile_image_path"]
        )
    except:
        object = None

    if object:
        profile_image_pre_signed_url = minio.client.presigned_get_object(
            Config.MINIO_BUCKET,
            user["info"]["profile_image_path"],
            expires=timedelta(days=1),
        )

        await auth_crud.update_profile_pre_signed_url(
            user["employee_id"], profile_image_pre_signed_url, mongo_client
        )

    else:
        await auth_crud.update_profile_pre_signed_url(
            user["employee_id"], None, mongo_client
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
    res, emp = await employee_crud.get_employee_with_computed_fields(
        employee_id, mongo_client
    )
    pprint.pprint(emp)

    res = {
        "alert": [],
        **res,
    }

    monthly_absent_days = res["attendance"]["total_absent_days"]
    monthly_permission_days = res["leaves_and_permissions"]["monthly_permission_hours"]

    alert = []
    # FIXME: Store the rules in the database and fetch them here
    if monthly_absent_days > 1:
        alert.append(
            {
                "title": "Leave Exceeded",
                "description": "You have exceeded your monthly leave limit of {} days".format(
                    1
                ),
            }
        )
    alert.append(
        {
            "title": "Permission Exceeded",
            "description": "You have exceeded your monthly permission limit of {} hours".format(
                2
            ),
        }
    )

    res["alert"] = alert

    if emp["is_marketing_staff"]:
        res["basic_information"]["is_marketing_staff"] = emp["is_marketing_staff"]
        res["basic_information"]["marketing_manager"] = emp["marketing_manager"]
    # pprint.pprint(res)
    return res


async def assign_role(role_req, mongo_client: AsyncIOMotorClient, payload):
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

    if role_req.type.value == "primary":
        update = await auth_crud.assign_primary_role(
            employee["employee_id"], role["_id"], mongo_client
        )

    elif role_req.type.value == "secondary":
        update = await auth_crud.assign_secondary_role(
            employee["employee_id"], role["_id"], mongo_client
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid Role Type")

    bind_key = None

    branch = employee["info"]["branch"].replace(" ", "_")

    if update:
        if role_req.role != "employee":
            if role_req.role == "HR":
                bind_key = "HR_{}".format(branch)
        elif role_req.role == "employee":
            bind_key = employee["employee_id"]

        mq = RabbitMQ()
        mq.ensure_queue("notifications_employee_{}".format(employee["uuid"]))
        mq.bind_queue(
            "notifications_employee_{}".format(employee["uuid"]),
            "employee_notification",
            bind_key,
        )

        notification = Notification(
            sender_id=payload["employee_id"],
            source="assign_role",
            mongo_client=mongo_client,
        )

        notifiers = [employee["employee_id"], "MD"]

        employee_notification = NotificationBase(
            title="Role Assigned",
            description="You have been assigned the role of {}".format(role_req.role),
            payload={},
            ui_action="read",
            type="employee",
            priority="high",
            source="assign_role",
            target=employee["employee_id"],
            meta=NotificationMeta(
                to=notifiers,
                from_=payload["employee_id"],
            ),
        )

        md_notification = NotificationBase(
            title="Role Assigned",
            description="{} has been assigned the role of {}".format(
                employee["info"]["name"], role_req.role
            ),
            payload={},
            ui_action="read",
            type="employee",
            priority="high",
            source="assign_role",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=payload["employee_id"],
            ),
        )

        send = SendNotification(notifier=[employee_notification, md_notification])

        await notification.send_notification(send)

        return True

    return False


async def remove_role(role_req, mongo_client: AsyncIOMotorClient, payload):
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

    if role_req.type.value == "primary":
        update = await auth_crud.remove_primary_role(
            employee["employee_id"], role["_id"], mongo_client
        )

    elif role_req.type.value == "secondary":
        update = await auth_crud.remove_secondary_role(
            employee["employee_id"], role["_id"], mongo_client
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid Role Type")
    bind_key = None

    if update:
        if role_req.role != "employee":
            bind_key = role_req.role
            if role_req.role == "HR":
                bind_key = "HR_{}".format(employee["info"]["branch"].replace(" ", "_"))
        elif role_req.role == "employee":
            bind_key = employee["employee_id"]

        mq = RabbitMQ()
        mq.ensure_queue("notifications_employee_{}".format(employee["uuid"]))
        mq.unbind_queue(
            "notifications_employee_{}".format(employee["uuid"]),
            "employee_notification",
            bind_key,
        )

        notification = Notification(
            sender_id=payload["employee_id"],
            source="remove_role",
            mongo_client=mongo_client,
        )

        notifiers = [employee["employee_id"], "MD"]

        employee_notification = NotificationBase(
            title="Role Removed",
            description="Your role of {} has been removed".format(role_req.role),
            payload={},
            ui_action="read",
            type="employee",
            priority="high",
            source="remove_role",
            target=employee["employee_id"],
            meta=NotificationMeta(
                to=notifiers,
                from_=payload["employee_id"],
            ),
        )

        md_notification = NotificationBase(
            title="Role Removed",
            description="{}'s role of {} has been removed".format(
                employee["info"]["name"], role_req.role
            ),
            payload={},
            ui_action="read",
            type="employee",
            priority="high",
            source="remove_role",
            target="MD",
            meta=NotificationMeta(
                to=notifiers,
                from_=payload["employee_id"],
            ),
        )

        send = SendNotification(notifier=[employee_notification, md_notification])

        await notification.send_notification(send)
        return True

    return False


async def compute_attendance(
    self,
    employee_id,
    month,
    mongo_client: AsyncIOMotorClient,
):
    attendance = await attendance_crud.get_attendance(employee_id, month, mongo_client)

    total_working_days = total_present_days = total_absent_days = 0

    for day in attendance:
        if day["is_holiday"]:
            total_working_days += 1
            continue

        if day["is_present"]:
            total_working_days += 1
            total_present_days += 1
        else:
            total_working_days += 1
            total_absent_days += 1

    present_percentage = (total_present_days / total_working_days) * 100

    return {
        "total_working_days": total_working_days,
        "total_present_days": total_present_days,
        "total_absent_days": total_absent_days,
        "present_percentage": present_percentage,
    }
