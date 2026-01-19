from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.services.user_context import JWTAuthUser
from app.tools.analytics_tools import (
    analyze_spendings,
    get_average_spending,
    get_spending_trends,
    get_top_merchants,
)
from app.utils.enums import BudgetPeriod

router = APIRouter(prefix="/analytics")

auth = JWTAuthUser()


@router.get("/analyze")
async def analyze(
    user_id: str = Depends(auth),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    try:
        res = await analyze_spendings(
            user_id,
            start_date,
            end_date,
        )
        return {"success": True, "response": res}
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Failed to analyze spendings {e}"
        ) from e


@router.get("/trends")
async def spending_trends(
    user_id: str = Depends(auth),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    try:
        res = await get_spending_trends(
            user_id,
            start_date,
            end_date,
        )
        return {"success": True, "response": res}
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Failed to get spendings trends {e}"
        ) from e


@router.get("/average")
async def average_spendings(
    user_id: str = Depends(auth), period: Optional[BudgetPeriod] = BudgetPeriod.YEARLY
):
    try:
        res = await get_average_spending(
            user_id=user_id,
            period=period,
        )
        return {"success": True, "response": res}
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Failed to get average spendings {e}",
        ) from e


@router.get("/top")
async def top_merchants(
    user_id: str = Depends(auth),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit=10,
):
    try:
        res = await get_top_merchants(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        return {"success": True, "response": res}
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Failed to get average spendings {e}",
        ) from e
