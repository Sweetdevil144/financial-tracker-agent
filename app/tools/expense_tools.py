from typing import Any, List, Mapping

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.agents.agent import Agent
from app.database.core_data import query_read, update_one
from app.models.agent import ExpenseResponse
from app.models.collections import Expenses
from app.utils.constants import Collection
from app.utils.log import logger


async def add_expense(user_id: str, text: str) -> ExpenseResponse:
    if not text:
        logger.error("Error processing text")
        return ExpenseResponse(
            _id="",
            success=False,
            message="No Text Provided for expense parsing",
            expense_id=None,
        )
    try:
        agent = Agent()

        parsed_expense = await agent.parse_expense(user_prompt=text, user_id=user_id)
        if not parsed_expense.user_id:
            parsed_expense.user_id = user_id
        logger.info(f"Expense parsed for user {user_id}: {parsed_expense}")

        expense = await agent.process_expense(parsed_data=parsed_expense)
        logger.info(f"Expense added for user {user_id}: {expense}")

        return expense
    except Exception as e:
        logger.error(f"Error adding expense: {str(e)}")
        return ExpenseResponse(
            _id="",success=False, message=f"Failed to add expense: {str(e)}", expense_id=None
        )


async def list_expenses(
    user_id: str,
    start_date: str,
    end_date: str,
    category: str,
    min_amount: int,
    max_amount: int,
    limit: int,
    sort_by: str = "asc",
) -> List[Expenses]:
    pipeline = [
        {
            "$search": {
                "index": "default",
                "compound": {
                    "filter": [
                        {"equals": {"path": "user_id", "value": user_id}},
                        {"equals": {"path": "deleted", "value": False}},
                        {
                            "text": {
                                "path": "category",
                                "query": category,
                                "fuzzy": {},
                            }
                        },
                        {
                            "range": {
                                "path": "amount",
                                "gte": min_amount,
                                "lte": max_amount,
                            }
                        },
                        {"range": {"path": "date", "gte": start_date, "lte": end_date}},
                    ]
                },
                "sort": {"amount": 1 if sort_by == "asc" else -1},
            }
        },
        {"$limit": limit},
    ]

    res = await query_read(collection_name=Collection.EXPENSES, aggregate=pipeline)
    logger.info(f"Query Read Expenses : {res}")
    return [Expenses(**doc) for doc in res]


async def update_expense(
    user_id: str, expense_id: str, update_fields: dict[str, Any]
) -> Mapping[str, Any] | None:
    try:
        filter = {"user_id": user_id, "_id": expense_id}

        res = await update_one(
            collection_name=Collection.EXPENSES,
            filter=filter,
            update={"$set": update_fields},
        )
        return res.raw_result
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to Update Expense : {str(e)}",
            status_code=HTTP_400_BAD_REQUEST,
        ) from e


async def delete_expense(user_id: str, expense_id: str) -> Mapping[str, Any] | None:
    try:
        filter = {"user_id": user_id, "_id": expense_id, "deleted": False}
        res = await update_one(
            collection_name=Collection.EXPENSES,
            filter=filter,
            update={"$set": {"deleted": True}},
        )

        return res.raw_result
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to Delete Expense : {str(e)}",
            status_code=HTTP_400_BAD_REQUEST,
        ) from e
