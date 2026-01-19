from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_502_BAD_GATEWAY

from app.models.expenses import CreateExpense, UpdateOne
from app.services.user_context import JWTAuthUser
from app.tools.expense_tools import (
    add_expense,
    delete_expense,
    list_expenses,
    list_individual_expense,
    update_expense,
)

router = APIRouter(prefix="/expenses")

auth = JWTAuthUser()


@router.post("/")
async def create_expense(request: CreateExpense, user_id: str = Depends(auth)):
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
async def list(
    user_id: str = Depends(auth),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None,
    limit: Optional[int] = 10,
    sort_by: Optional[str] = "asc",
):
    try:
        expenses = await list_expenses(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=limit,
            sort_by=sort_by,
        )
        return {"expenses": expenses, "count": len(expenses)}
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Failed to list expenses \t {e}"
        ) from e


@router.get("/{expense_id}")
async def list_one(expense_id: str, user_id: str = Depends(auth)):
    try:
        expense = await list_individual_expense(user_id=user_id, expense_id=expense_id)
        return {
            "expense": expense,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Failed to list expense {e}"
        ) from e


@router.put("/{expense_id}")
async def update(request: UpdateOne, expense_id: str, user_id: str = Depends(auth)):
    try:
        res = await update_expense(
            user_id=user_id,
            expense_id=expense_id,
            update_fields=request.update_fields,
        )
        return {
            "success": res.acknowledged,
            "matched": res.matched_count,
            "modified": res.modified_count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_502_BAD_GATEWAY, detail=f"Failed to Update Expense {e}"
        ) from e


@router.delete("/{expense_id}")
async def delete(expense_id: str, user_id: str = Depends(auth)):
    try:
        res = await delete_expense(user_id=user_id, expense_id=expense_id)
        return {
            "success": res.acknowledged,
            "matched": res.matched_count,
            "modified": res.modified_count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_502_BAD_GATEWAY, detail=f"Failed to Delete Expense {e}"
        ) from e
