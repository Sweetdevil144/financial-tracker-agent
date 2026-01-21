from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

from app.database.core_data import query_read
from app.utils.constants import Collection
from app.utils.enums import BudgetPeriod


async def analyze_spendings(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict[str, Any]]:
    if end_date is None:
        end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if start_date is None:
        start_date = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")

    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "deleted": False,
                "date": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
            }
        },
        {
            "$sort": {"total": -1},
        },
    ]

    res = await query_read(collection_name=Collection.EXPENSES, aggregate=pipeline)
    grand_total = sum(item["total"] for item in res)
    for item in res:
        item["percentage"] = (
            round((item["total"] / grand_total) * 100, 2) if grand_total > 0 else 0
        )
    return res


async def get_top_merchants(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10,
) -> List[dict[str, Any]]:
    if end_date is None:
        end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if start_date is None:
        start_date = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "deleted": False,
                "date": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$group": {
                "_id": "$merchant",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"total": -1}},
        {"$limit": limit},
    ]

    return await query_read(collection_name=Collection.EXPENSES, aggregate=pipeline)


async def get_spending_trends(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict[str, Any]]:
    if end_date is None:
        end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if start_date is None:
        start_date = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")

    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "deleted": False,
                "date": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": {"$dateFromString": {"dateString": "$date"}}},
                    "month": {"$month": {"$dateFromString": {"dateString": "$date"}}},
                },
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}},
    ]
    return await query_read(collection_name=Collection.EXPENSES, aggregate=pipeline)


async def get_average_spending(
    user_id: str, period: Optional[BudgetPeriod] = BudgetPeriod.YEARLY
):
    if period == BudgetPeriod.YEARLY:
        group_id = {"year": {"$year": {"$dateFromString": {"dateString": "$date"}}}}
    elif period == BudgetPeriod.MONTHLY:
        group_id = {
            "year": {"$year": {"$dateFromString": {"dateString": "$date"}}},
            "month": {"$month": {"$dateFromString": {"dateString": "$date"}}},
        }
    elif period == BudgetPeriod.WEEKLY:
        group_id = {
            "year": {"$year": {"$dateFromString": {"dateString": "$date"}}},
            "week": {"$isoWeek": {"$dateFromString": {"dateString": "$date"}}},
        }
    else:
        group_id = {
            "year": {"$year": {"$dateFromString": {"dateString": "$date"}}},
            "month": {"$month": {"$dateFromString": {"dateString": "$date"}}},
            "day": {"$dayOfMonth": {"$dateFromString": {"dateString": "$date"}}},
        }
    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "deleted": False,
            }
        },
        {"$group": {"_id": group_id, "period_total": {"$sum": "$amount"}}},
        {
            "$group": {
                "_id": None,
                "average": {"$avg": "$period_total"},
                "periods_count": {"$sum": 1},
            }
        },
    ]
    expenses = await query_read(collection_name=Collection.EXPENSES, aggregate=pipeline)
    if expenses:
        return expenses[0]
    return {"average": 0, "periods_count": 0}
