from app.api.routes.employees import router as employees_router
from app.api.routes.salary import router as salary_router
from app.api.routes.leave import router as leave_router
from app.api.routes.loan import router as loan_router
from app.api.routes.auth import router as auth_router
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(employees_router, prefix="/employees", tags=["employees"])
api_router.include_router(salary_router, prefix="/salary", tags=["salary"])
api_router.include_router(leave_router, prefix="/leave", tags=["leave"])
api_router.include_router(loan_router, prefix="/loan", tags=["loan"])
