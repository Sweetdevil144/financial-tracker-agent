from typing import Any, List

from fastapi import HTTPException
from pymongo.results import InsertOneResult, UpdateResult
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.database.core_data import insert_one, query_read, update_one
from app.models.collections import Budgets
from app.utils.constants import Collection


async def create_budget(budget_data: Budgets) -> InsertOneResult:
    try:
        return await insert_one(
            collection_name=Collection.BUDGETS,
            document=budget_data.model_dump(by_alias=True),
        )
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to insert Budget : {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_budgets(user_id: str) -> List[Budgets]:
    try:
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "deleted": False,
                }
            },
            {
                "$sort": {"amount": -1},
            },
        ]
        res = await query_read(collection_name=Collection.BUDGETS, aggregate=pipeline)
        return [Budgets(**doc) for doc in res]
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to GET Budget : {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def update_budget(
    user_id: str, budget_id: str, update_fields: dict
) -> UpdateResult:
    try:
        filters = {"user_id": user_id, "_id": budget_id, "deleted": False}
        res = await update_one(
            collection_name=Collection.BUDGETS,
            update={"$set": update_fields},
            filter=filters,
        )
        return res
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to Update Budget : {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def delete_budget(user_id: str, budget_id: str) -> UpdateResult:
    try:
        filters = {"user_id": user_id, "_id": budget_id, "deleted": False}
        res = await update_one(
            collection_name=Collection.BUDGETS,
            update={"$set": {"deleted": True}},
            filter=filters,
        )
        return res
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to Update Budget : {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_budget_status(user_id: str) -> List[dict[str, Any]]:
    budgets = await get_all_user_budgets(user_id=user_id)
    result = []
    try:
        for budget in budgets:
            expense_pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "category": budget.category,
                        "deleted": False,
                        "date": {"$gte": budget.start_date, "$lte": budget.end_date},
                    },
                },
                {"$group": {"_id": None, "total_spent": {"$sum": "$amount"}}},
            ]
            res = await query_read(
                collection_name=Collection.EXPENSES, aggregate=expense_pipeline
            )
            spent = res[0]["total_spent"] if res else 0
            utilization = (spent / budget.amount) * 100 if budget.amount > 0 else 0
            result.append(
                {
                    "budget_id": budget.id,
                    "category": budget.category,
                    "period": budget.period.value,
                    "budget_amount": budget.amount,
                    "currency": budget.currency.value,
                    "spent": round(spent, 2),
                    "remaining": round(budget.amount - spent, 2),
                    "utilization": round(utilization, 2),
                    "warning": utilization > 80,
                    "exceeded": utilization > 100,
                    "start_date": str(budget.start_date),
                    "end_date": str(budget.end_date),
                }
            )
        return result
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to GET Budget Status : {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_all_user_budgets(user_id: str) -> List[Budgets]:
    pipeline = [
        {"$match": {"user_id": user_id, "deleted": False}},
        {"$sort": {"created_at": -1}},
    ]
    res = await query_read(collection_name=Collection.BUDGETS, aggregate=pipeline)
    return [Budgets(**doc) for doc in res]
