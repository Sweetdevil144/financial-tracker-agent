from typing import Any, List

from app.database.core_data import query_read
from app.utils.constants import Collection


async def analyze_spendings(
    user_id: str, start_date: str, end_date: str
) -> List[dict[str, Any]]:
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
    user_id: str, start_date: str, end_date: str, limit: int = 10
) -> List[dict[str, Any]]:
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
    user_id: str, start_date: str, end_date: str
) -> List[dict[str, Any]]:
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
                "_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}},
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"$_id.year": 1, "$_id.month": 1}},
    ]
    return await query_read(collection_name=Collection.EXPENSES, aggregate=pipeline)
