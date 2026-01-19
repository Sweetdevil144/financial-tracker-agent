from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.models.budgets import DeleteOne, UpdateOne
from app.models.collections import Budgets
from app.services.user_context import JWTAuthUser
from app.tools.budget_tools import (
    create_budget,
    delete_budget,
    get_all_user_budgets,
    get_budget_status,
    update_budget,
)

router = APIRouter(prefix="/expenses")

auth = JWTAuthUser()


@router.post("/")
async def create(
    request: Budgets,
    user_id: str = Depends(auth),
):
    try:
        request.user_id = user_id
        res = await create_budget(request)

        return {
            "success": True if res.inserted_id else False,
            "response": res,
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


@router.put("/")
async def update(request: UpdateOne, user_id: str = Depends(auth)):
    try:
        res = await update_budget(
            user_id=user_id,
            budget_id=request.budget_id,
            update_fields=request.update_fields,
        )
        return {
            "success": True if res.did_upsert else False,
            "res": res,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Failed to Update Budget {e}"
        ) from e


@router.delete("/")
async def delete(request: DeleteOne, user_id: str = Depends(auth)):
    try:
        res = await delete_budget(
            user_id=user_id,
            budget_id=request.budget_id,
        )
        return {
            "success": True if res.did_upsert else False,
            "res": res,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Failed to Delete Budget {e}"
        ) from e


@router.get("/status")
async def get_status(user_id: str = Depends(auth)):
    try:
        res = await get_budget_status(user_id)

        return {"status": res}
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Failed to Delete Budget {e}"
        ) from e
