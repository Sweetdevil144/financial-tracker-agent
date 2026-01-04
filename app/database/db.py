from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import config
from app.utils.log import logger


class Database:
    # MongoDB client - initialized lazily
    _client: AsyncIOMotorClient | None = None
    _db: AsyncIOMotorDatabase | None = None

    ASCENDING = 1
    """Ascending sort order."""
    DESCENDING = -1
    """Descending sort order."""

    @staticmethod
    async def connect() -> None:
        Database._client = AsyncIOMotorClient(config.MONGO_URI)
        Database._db = Database._client[config.DATABASE_NAME]
        logger.info("MongoDB client initialized Successfully")
        await Database.create_indexes()

    @staticmethod
    async def disconnect() -> None:
        if Database._client is not None:
            Database._client.close()
            Database._client = None
            Database._db = None
            logger.info("MongoDB client disconnected")
        else:
            raise ConnectionError("Client not connected")

    @staticmethod
    def get_client():
        """Get the MongoDB client, initializing if needed."""
        if Database._client is None:
            if not config.MONGO_URI:
                logger.warning("MONGO_URI not set - MongoDB features will be disabled")
                return None
            Database._client = AsyncIOMotorClient(config.MONGO_URI)
            logger.info("MongoDB client initialized")
        return Database._client

    @staticmethod
    def get_database():
        """Get the MongoDB database, initializing if needed."""
        if Database._db is None:
            client = Database.get_client()
            if client is None:
                return None
            if not config.DATABASE_NAME:
                logger.warning(
                    "DATABASE_NAME not set - MongoDB features will be disabled"
                )
                return None
            Database._db = client.get_database(config.DATABASE_NAME)
            logger.info(f"Connected to database: {config.DATABASE_NAME}")
        return Database._db

    @staticmethod
    async def create_indexes():
        """Create indexes for collections."""
        db = Database.get_database()
        if db is None:
            return
        await db["expenses"].create_index(
            [("user_id", Database.ASCENDING), ("date", Database.DESCENDING)]
        )
        await db["users"].create_index([("name", Database.ASCENDING)])
        await db["preferences"].create_index(
            [("user_id", Database.ASCENDING), ("email", Database.ASCENDING)]
        )
        await db["budgets"].create_index(
            [("user_id", Database.ASCENDING), ("category", Database.ASCENDING)]
        )
        logger.info("Indexes created")
