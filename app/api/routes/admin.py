from fastapi import APIRouter, Depends, Response, Request, HTTPException
from app.database import get_mongo, AsyncIOMotorClient


from app.schemas.admin import (
    Rules,
    Guidelines,
    ReportType,
    BankSalaryBatchCreateRequest,
    BankSalaryBatchCreateResponse,
)

from app.api.controllers.admin import AdminController

from app.api.utils.auth import role_required

from app.api.controllers import auth as auth_controller

from app.schemas.auth import (
    AssignRoleReq,
    RemoveRoleReq,
)


from app.api.utils.employees import verify_login_token, verify_custom_master_token

router = APIRouter()


@router.get("/rules/meta")
async def get_rules_meta(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.get_rules_meta()

    return {"message": "Rules meta fetched successfully", "data": res}


@router.get("/rules")
async def get_rules(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.get_rules()

    return {"message": "Rules fetched successfully", "data": res}


@router.put("/rules")
async def post_rules(
    rules: Rules,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.post_rules(rules)

    if res:
        return {"message": "Rules created successfully"}

    return {"message": "Rules creation failed"}


@router.get("/guidelines")
async def get_guidelines(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.get_guidelines()

    return {"message": "Guidelines fetched successfully", "data": res}


@router.put("/guidelines")
async def post_guidelines(
    guidelines: Guidelines,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.post_guidelines(guidelines)

    if res:
        return {"message": "Guidelines created successfully"}

    return {"message": "Guidelines creation failed"}


@router.get("/roles")
async def get_roles(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.get_roles()

    if res:
        return {"message": "Roles fetched successfully", "data": res}

    return {"message": "Roles fetching failed"}


@router.get("/roles/{employee_id}")
async def get_employee_role(
    employee_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.get_employee_role(employee_id)

    return {"data": res}


# FIXME: Assign role and remove role should be restricted, use a separate validator to accept both JWT and Custom Token for backend Uses
@router.post("/roles")
@role_required(["MD"])
async def assign_role(
    role_request: AssignRoleReq,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_custom_master_token),
):
    res = await auth_controller.assign_role(role_request, mongo_client, payload)

    if res:
        return {
            "status_code": 200,
        }

    raise HTTPException(status_code=400, detail="Role assignment failed")


# FIXME: Assign role and remove role should be restricted, use a separate validator to accept both JWT and Custom Token for backend Uses
@router.put("/remove-role")
@role_required(["MD"])
async def remove_role(
    role_request: RemoveRoleReq,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_custom_master_token),
):
    res = await auth_controller.remove_role(role_request, mongo_client, payload)

    if res:
        return {
            "status_code": 200,
        }

    raise HTTPException(status_code=400, detail="Role deletion failed")


@router.get("/report/meta")
async def get_report_meta(
    type: ReportType = None,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.get_report_meta(type)

    return {"message": "Report meta fetched successfully", "data": res}


@router.post("/report/bank_salary/batch")
async def create_bank_salary_batch(
    BankSalaryBatchCreateRequest: BankSalaryBatchCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.create_bank_salary_batch(BankSalaryBatchCreateRequest)
    return BankSalaryBatchCreateResponse(
        message="Bank salary batch created successfully", status=True, data=res
    )


@router.get("/report/bank_salary/batch/{batch_id}")
async def get_bank_salary_batch(
    batch_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.get_bank_salary_batch(batch_id)
    return BankSalaryBatchCreateResponse(
        message="Bank salary batch fetched successfully", status=True, data=res
    )


@router.get("/report/bank_salary/batch")
async def get_bank_salary_batch_list(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.get_bank_salary_batch_list()
    # return BankSalaryBatchCreateResponse(message="Bank salary batch list fetched successfully",status=True,data=res)
    return {"data": res}


@router.put("/report/bank_salary/batch/{batch_id}")
async def update_bank_salary_batch(
    batch_id: str,
    BankSalaryBatchCreateRequest: BankSalaryBatchCreateRequest,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""
    obj = AdminController(payload, mongo_client)
    res = await obj.update_bank_salary_batch(batch_id, BankSalaryBatchCreateRequest)
    return BankSalaryBatchCreateResponse(
        message="Bank salary batch updated successfully", status=True, data=res
    )


@router.delete("/report/bank_salary/batch/{batch_id}")
async def delete_bank_salary_batch(
    batch_id: str,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo),
    payload: dict = Depends(verify_login_token),
):
    """Create a new location entry"""

    obj = AdminController(payload, mongo_client)
    res = await obj.delete_bank_salary_batch(batch_id)
    # return BankSalaryBatchCreateResponse(message="Bank salary batch deleted successfully",status=True,data=res)
    return {"message": "Bank salary batch deleted successfully"}
