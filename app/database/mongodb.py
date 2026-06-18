"""
MongoDB database connection and initialization module.
Provides async Motor client and database instance.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, TEXT
from app.utils.logger import get_logger

logger = get_logger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "shopping_list_db")


class MongoDB:
    """Manages the MongoDB connection lifecycle."""

    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        """Open the MongoDB connection and create indexes."""
        logger.info("Connecting to MongoDB...")
        cls.client = AsyncIOMotorClient(MONGO_URI)
        cls.db = cls.client[DATABASE_NAME]
        await cls._create_indexes()
        logger.info("Connected to MongoDB successfully.")

    @classmethod
    async def disconnect(cls):
        """Close the MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB.")

    @classmethod
    async def _create_indexes(cls):
        """Create indexes for efficient lookups."""
        # Shopping lists: text index on name for search, unique name
        await cls.db.shopping_lists.create_index([("name", TEXT)])
        await cls.db.shopping_lists.create_index([("created_at", ASCENDING)])
        await cls.db.shopping_lists.create_index([("is_deleted", ASCENDING)])

        # Shopping items: compound index on list_id + item_id
        await cls.db.shopping_items.create_index([("list_id", ASCENDING)])
        await cls.db.shopping_items.create_index([("list_id", ASCENDING), ("name", TEXT)])
        await cls.db.shopping_items.create_index([("is_deleted", ASCENDING)])
        logger.info("MongoDB indexes created.")

    @classmethod
    def get_db(cls):
        """Return the database instance."""
        return cls.db


db_instance = MongoDB()


async def get_database():
    """Dependency: returns the active database."""
    return MongoDB.get_db()
