"""
Repository layer for Shopping List MongoDB operations.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from bson import ObjectId
from bson.errors import InvalidId
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _to_response(doc: dict) -> dict:
    """Convert a MongoDB document to a serializable dict."""
    doc["id"] = str(doc.pop("_id"))
    doc.pop("is_deleted", None)
    return doc


class ShoppingListRepository:
    """Handles all MongoDB operations for shopping lists."""

    def __init__(self, db):
        self.collection = db["shopping_lists"]

    async def create(self, data: dict) -> dict:
        """
        Insert a new shopping list document.

        Args:
            data: Dictionary of shopping list fields.

        Returns:
            The created document with string id.
        """
        data["is_deleted"] = False
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return _to_response(doc)

    async def get_all(
        self,
        page: int,
        page_size: int,
        search: Optional[str] = None,
    ) -> Tuple[List[dict], int]:
        """
        Retrieve all non-deleted shopping lists with optional name search and pagination.

        Args:
            page: Page number (1-based).
            page_size: Number of results per page.
            search: Optional substring to filter by name.

        Returns:   
            Tuple of (list of documents, total count).
        """
        query: dict = {"is_deleted": False}
        if search:
            query["$text"] = {"$search": search}

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        docs = [_to_response(doc) async for doc in cursor]
        return docs, total

    async def get_by_id(self, list_id: str) -> Optional[dict]:
        """
        Retrieve a single non-deleted shopping list by ID.

        Args:
            list_id: The string ObjectId of the list.

        Returns:
            Document dict or None if not found.
        """
        try:
            oid = ObjectId(list_id)
            doc = await self.collection.find_one({"_id": oid, "is_deleted": False})
            return _to_response(doc) if doc else None
        except InvalidId:
            logger.error(f"invalid id")
            return None

        except Exception as e:
            logger.error(f"unexpected error {str(e)}")
            return None


    async def update(self, list_id: str, data: dict) -> Optional[dict]:
        """
        Update fields of an existing shopping list.

        Args:
            list_id: The string ObjectId of the list.
            data: Fields to update.

        Returns:
            Updated document dict or None if not found.
        """
        try:
            oid = ObjectId(list_id)
        except InvalidId:
            return None
        data["updated_at"] = datetime.utcnow()
        result = await self.collection.find_one_and_update(
            {"_id": oid, "is_deleted": False},
            {"$set": data},
            return_document=True,
        )
        return _to_response(result) if result else None

    async def soft_delete(self, list_id: str) -> bool:
        """
        Soft-delete a shopping list by setting is_deleted=True.

        Args:
            list_id: The string ObjectId of the list.

        Returns:
            True if deleted, False if not found.
        """
        try:
            oid = ObjectId(list_id)
        except InvalidId:
            return False
        result = await self.collection.update_one(
            {"_id": oid, "is_deleted": False},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count > 0
