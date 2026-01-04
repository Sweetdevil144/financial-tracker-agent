from typing import Any, List, Mapping, Optional, Union

from pymongo.results import (
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)

from app.database.db import Database


async def update_one(
    collection_name: str,
    filter: Mapping[str, Any],
    update: Mapping[str, Any],
    upsert: bool = False,
) -> UpdateResult:
    """
    Update a single document in MongoDB.

    Args:
        collection_name: Name of the collection to update
        filter: Filter criteria to match the document
        update: Update operations (e.g. {"$set": {...}})
        upsert: Whether to insert a new document if no match is found

    Returns:
        UpdateResult with information about the update operation

    Raises:
        RuntimeError: If MongoDB is not configured
    """
    db = Database.get_database()
    if db is None:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGO_URI and DATABASE_NAME environment variables."
        )

    collection = db.get_collection(collection_name)

    res = await collection.update_one(filter=filter, update=update, upsert=upsert)
    return res


async def delete(collection_name: str, filter: Mapping[str, Any]) -> DeleteResult:
    """
    Delete documents from a MongoDB collection.

    Args:
        collection_name: Name of the collection to delete from
        filter: Filter criteria to match documents for deletion

    Returns:
        DeleteResult containing information about deleted documents

    Raises:
        RuntimeError: If MongoDB is not configured
    """
    db = Database.get_database()
    if db is None:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGO_URI and DATABASE_NAME environment variables."
        )

    collection = db.get_collection(collection_name)

    res = await collection.delete_many(filter=filter)

    return res


async def insert_one(
    document: dict[str, Any],
    collection_name: str,
) -> InsertOneResult:
    """
    Insert one document into MongoDB.

    Args:
        document: Document to be inserted
        collection_name: Name of the collection to query

    Returns:
        The matching document or empty dict if not found

    Raises:
        RuntimeError: If MongoDB is not configured
    """
    db = Database.get_database()
    if db is None:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGO_URI and DATABASE_NAME environment variables."
        )

    collection = db.get_collection(collection_name)

    res = await collection.insert_one(document)
    return res


async def insert_many(
    documents: List[dict[str, Any]],
    collection_name: str,
) -> InsertManyResult:
    """
    Insert multiple documents into MongoDB.

    Args:
        document: Document to be inserted
        collection_name: Name of the collection to query

    Returns:
        The matching document or empty dict if not found

    Raises:
        RuntimeError: If MongoDB is not configured
    """
    db = Database.get_database()
    if db is None:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGO_URI and DATABASE_NAME environment variables."
        )

    collection = db.get_collection(collection_name)

    res = await collection.insert_many(documents=documents)
    return res


async def read_one(
    collection_name: str,
    data_filter: Union[dict[str, Any], str],
    options: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Read one document from MongoDB.

    Args:
        collection_name: Name of the collection to query
        data_filter: Filter criteria for the query
        options: Projection options (fields to include/exclude)

    Returns:
        The matching document or empty dict if not found

    Raises:
        RuntimeError: If MongoDB is not configured
    """
    db = Database.get_database()
    if db is None:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGO_URI and DATABASE_NAME environment variables."
        )

    collection = db.get_collection(collection_name)

    model = await collection.find_one(data_filter, options)
    return model or {}


async def query_read(
    collection_name: str, aggregate: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Execute an aggregation pipeline on MongoDB.

    Args:
        collection_name: Name of the collection to query
        aggregate: Aggregation pipeline stages

    Returns:
        List of documents from the aggregation result

    Raises:
        RuntimeError: If MongoDB is not configured
    """
    db = Database.get_database()
    if db is None:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGO_URI and DATABASE_NAME environment variables."
        )

    collection = db.get_collection(collection_name)

    if not aggregate:
        aggregate = []

    return await collection.aggregate(aggregate).to_list(None)


@staticmethod
async def list_collections() -> List[str]:
    """List all collections in the database."""
    db = Database.get_database()
    if db is None:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGO_URI and DATABASE_NAME environment variables."
        )

    return await db.list_collection_names()
