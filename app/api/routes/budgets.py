from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.models.budgets import CreateBudget, UpdateOne
from app.models.collections import Budgets
from app.services.user_context import JWTAuthUser
from app.tools.budget_tools import (
    create_budget,
    delete_budget,
    get_all_user_budgets,
    get_budget_status,
    update_budget,
)

router = APIRouter(prefix="/budgets")

auth = JWTAuthUser()


@router.get("/status")
async def get_status(user_id: str = Depends(auth)):
    try:
        res = await get_budget_status(user_id)
        return {"status": res}
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Failed to get Budget Status {e}"
        ) from e


@router.post("/")
async def create(
    request: CreateBudget,
    user_id: str = Depends(auth),
):
    try:
        budget = Budgets(
            _id=str(uuid4()),
            user_id=user_id,
            category=request.category,
            amount=request.amount,
            currency=request.currency,
            period=request.period,
            start_date=request.start_date,
            end_date=request.end_date,
            description=request.description,
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        )
        res = await create_budget(budget)

        return {
            "success": True if res.inserted_id else False,
            "budget_id": str(res.inserted_id) if res.inserted_id else None,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Failed to create Budget {e}"
        ) from e


@router.get("/")
async def get_budgets(user_id: str = Depends(auth)):
    try:
        budgets = await get_all_user_budgets(user_id)
        return {"success": True if len(budgets) > 0 else False, "budgets": budgets}
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Failed to GET Budget {e}"
        ) from e


@router.put("/{budget_id}")
async def update(request: UpdateOne, budget_id: str, user_id: str = Depends(auth)):
    try:
        res = await update_budget(
            user_id=user_id,
            budget_id=budget_id,
            update_fields=request.update_fields,
        )
        return {
            "success": res.modified_count > 0,
            "matched": res.matched_count,
            "modified": res.modified_count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Failed to Update Budget {e}"
        ) from e


@router.delete("/{budget_id}")
async def delete(budget_id: str, user_id: str = Depends(auth)):
    try:
        res = await delete_budget(
            user_id=user_id,
            budget_id=budget_id,
        )
        return {
            "success": res.modified_count > 0,
            "matched": res.matched_count,
            "modified": res.modified_count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Failed to Delete Budget {e}"
        ) from e
