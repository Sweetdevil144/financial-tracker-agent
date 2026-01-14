from typing import List

from fastapi import HTTPException
from pymongo.results import InsertOneResult, UpdateResult
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.database.core_data import insert_one, query_read, update_one
from app.models.collections import Budgets
from app.utils.constants import Collection


async def create_budget(budget_data: Budgets) -> InsertOneResult:
    try:
        return await insert_one(
            collection_name=Collection.BUDGETS, document=budget_data.model_dump()
        )
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to insert Budget : {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_budgets(user_id: str, start_date: str, end_date: str) -> List[Budgets]:
    try:
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "date": {"$gte": start_date, "$lte": end_date},
                    "deleted": False
                }
            },
            {
                "$sort": {"total": -1},
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
        filters = {"user_id": user_id, "budget_id": budget_id, "deleted": False}
        res = await update_one(
            collection_name=Collection.BUDGETS, update=update_fields, filter=filters
        )
        return res
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to Update Budget : {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def delete_budget(user_id: str, budget_id: str) -> UpdateResult:
    try:
        filters = {"user_id": user_id, "budget_id": budget_id, "deleted": False}
        res = await update_one(
            collection_name=Collection.BUDGETS, update={"deleted": True}, filter=filters
        )
        return res
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to Update Budget : {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )
