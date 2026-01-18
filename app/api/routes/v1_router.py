from fastapi import APIRouter
from api.routes.expenses import router as expense_router
# from api.routes.budgets import router as health_router

v1_router = APIRouter(prefix='/v1')

v1_router.include_router(expense_router)

