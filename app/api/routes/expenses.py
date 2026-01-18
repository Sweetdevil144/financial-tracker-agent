from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.models.expenses import (
    CreateExpenseRequest,
    ListExpenseRequest,
    ListIndividualExpenseRequest,
)
from app.services.user_context import JWTAuthUser
from app.tools.expense_tools import add_expense, list_expenses, list_individual_expense

router = APIRouter(prefix="/expenses")

auth = JWTAuthUser()


@router.post("/")
async def create_expense(request: CreateExpenseRequest, user_id: str = Depends(auth)):
    text = request.text
    if request.amount:
        text += f"Amount = {request.amount}."
    if request.category:
        text += f"Payment Category = {request.category}."
        if request.currency:
            text += f"My Native currency = {request.currency}"
    response = await add_expense(user_id=user_id, text=text)
    return response


@router.get("/")
async def list_expense(request: ListExpenseRequest, user_id: str = Depends(auth)):
    try:
        expenses = await list_expenses(
            user_id=user_id,
            start_date=request.start_date,
            end_date=request.end_date,
            category=request.category,
            min_amount=request.min_amount,
            max_amount=request.max_amount,
            limit=request.limit,
            sort_by=request.sort_by,
        )
        return {"expenses": expenses, "count": len(expenses)}
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Failed to list expenses \t {e}"
        ) from e


@router.get("/id")
async def list_single_expense(
    request: ListIndividualExpenseRequest, user_id: str = Depends(auth)
):
    try:
        expense = await list_individual_expense(
            user_id=user_id, expense_id=request.expense_id
        )
        return {
            "expense": expense,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Failed to list expense {e}"
        )
