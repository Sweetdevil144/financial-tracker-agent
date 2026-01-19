from typing import Any, List, Optional

from fastapi import HTTPException
from pymongo.results import UpdateResult
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_502_BAD_GATEWAY

from app.agents.agent import Agent
from app.database.core_data import query_read, update_one
from app.models.agent import ExpenseResponse
from app.models.collections import Expenses
from app.utils.constants import Collection
from app.utils.log import logger


async def add_expense(user_id: str, text: str) -> ExpenseResponse:
    if not text.strip():
        logger.error("Error processing text")
        return ExpenseResponse(
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
            success=False, message=f"Failed to add expense: {str(e)}", expense_id=None
        )


async def list_expenses(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None,
    limit: Optional[int] = 100,
    sort_by: Optional[str] = "asc",
) -> List[Expenses]:
    match_query = {
        "user_id": user_id,
        "deleted": False,
    }
    if start_date and end_date:
        match_query["date"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        match_query["date"] = {"$gte": start_date}
    elif end_date:
        match_query["date"] = {"$lte": end_date}

    if category:
        match_query["category"] = {"$regex": category, "$options": "i"}
    
    if not min_amount:
        min_amount = 0
    if not max_amount:
        max_amount = 999999999
    if min_amount > 0 or max_amount < 999999999:
        match_query["amount"] = {"$gte": min_amount, "$lte": max_amount}

    pipeline = [
        {"$match": match_query},
        {"$sort": {"amount": 1 if sort_by == "asc" else -1}},
        {"$limit": limit},
    ]

    res = await query_read(collection_name=Collection.EXPENSES, aggregate=pipeline)
    logger.info(f"Query Read Expenses : {res}")
    return [Expenses(**doc) for doc in res]


async def list_individual_expense(user_id: str, expense_id: str) -> Expenses:
    pipeline = [
        {"$match": {"user_id": user_id, "_id": expense_id}},
        {"$limit": 1},
    ]
    res = await query_read(collection_name=Collection.EXPENSES, aggregate=pipeline)
    logger.info(
        f"Query Read Single Expense, expense_id: {expense_id}, response: {res[0]}"
    )
    expense = Expenses(**res[0])
    return expense


async def update_expense(
    user_id: str, expense_id: str, update_fields: dict[str, Any]
) -> UpdateResult:
    try:
        filter = {"user_id": user_id, "_id": expense_id}

        res = await update_one(
            collection_name=Collection.EXPENSES,
            filter=filter,
            update={"$set": update_fields},
        )
        return res
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to Update Expense : {str(e)}",
            status_code=HTTP_502_BAD_GATEWAY,
        ) from e


async def delete_expense(user_id: str, expense_id: str) -> UpdateResult:
    try:
        filter = {"user_id": user_id, "_id": expense_id, "deleted": False}
        res = await update_one(
            collection_name=Collection.EXPENSES,
            filter=filter,
            update={"$set": {"deleted": True}},
        )

        return res
    except Exception as e:
        raise HTTPException(
            detail=f"Failed to Delete Expense : {str(e)}",
            status_code=HTTP_400_BAD_REQUEST,
        ) from e
