"""
Repository layer for Shopping Item MongoDB operations.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from bson import ObjectId
from bson.errors import InvalidId
from app.utils.logger import get_logger
from pymongo import ReturnDocument

logger = get_logger(__name__)


def _to_response(doc: dict) -> dict:
    """Convert a MongoDB document to a serializable dict."""
    doc["id"] = str(doc.pop("_id"))
    doc.pop("is_deleted", None)
    return doc


class ShoppingItemRepository:
    """Handles all MongoDB operations for shopping items."""

    def __init__(self, db):
        self.collection = db["shopping_items"]

    async def create(self, list_id: str, data: dict) -> Optional[dict]:
        """
        Insert a new shopping item document.

        Args:
            list_id: The parent shopping list ID.
            data: Dictionary of shopping item fields.

        Returns:
            The created document with string id.
        """
        try:
            document={**data,"list_id":list_id,"is_deleted":False}
            result=await self.collection.insert_one(document)
            doc=await self.collection.find_one({"_id":result.inserted_id})
            if doc:
                logger.info("item created succesfully")
                return _to_response(doc)
            logger.error(f"inserted item couldnot retrieved {list_id}")
            return None
        except Exception as e:
            logger.exception(f"failed to create shopping item {str(e)}")
            return None

        

    async def bulk_create(self, list_id: str, items: List[dict]) -> List[dict]:
        """
        Insert multiple shopping items at once.

        Args:
            list_id: The parent shopping list ID.
            items: List of item dicts to insert.

        Returns:
            List of created item documents.
        """
        try:
            documents=[
                {
                    **item,
                    "list_id":list_id,
                    "is_deleted":False,
                }
                for item in items
            ]
            result=await self.collection.insert_many(documents)
            docs=[]
            async for doc in self.collection.find({"_id":{"$in":result.inserted_ids}}):
                docs.append(_to_response(doc))
            return docs

        except Exception as e:
            logger.exception(f"failed to create bulk items {list_id}")
            return []

    async def get_all(
        self,
        list_id: str,
        page: int,
        page_size: int,
        search: Optional[str] = None,
    ) -> Tuple[List[dict], int]:
        """
        Retrieve all non-deleted items for a list with optional search and pagination.

        Args:
            list_id: The parent shopping list ID.
            page: Page number (1-based).
            page_size: Number of results per page.
            search: Optional substring to filter by name.

        Returns:
            Tuple of (list of item dicts, total count).
        """
        try:
            query: dict = {"list_id": list_id, "is_deleted": False}
            if search:
                query["$text"] = {"$search": search}

            total = await self.collection.count_documents(query)
            skip = (page - 1) * page_size
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            docs = [_to_response(doc) async for doc in cursor]
            return docs, total
        except Exception:
            logger.exception(f"failed to get shopping items {list_id}")
            raise

    async def get_by_id(self, list_id: str, item_id: str) -> Optional[dict]:
        """
        Retrieve a single non-deleted item by list ID and item ID.

        Args:
            list_id: The parent shopping list ID.
            item_id: The string ObjectId of the item.

        Returns:
            Item document dict or None if not found.
        """
        try:
            if not ObjectId.is_valid(item_id):
                logger.warning(f"Invalid ObjectId received: {item_id}")
                return None
            doc = await self.collection.find_one({"_id": ObjectId(item_id), "list_id": list_id, "is_deleted": False})
            if doc:
                logger.info(f"item fetched succesfully{item_id}")
                return _to_response((doc))
            logger.info(f"shoppping item not found {item_id}")
        except Exception:
            logger.exception(f"Failed to retrieve shopping item. item_id={item_id}")
            return None
        
    

    async def update(self, list_id: str, item_id: str, data: dict) -> Optional[dict]:
        """
        Update fields of an existing shopping item.

        Args:
            list_id: The parent shopping list ID.
            item_id: The string ObjectId of the item.
            data: Fields to update.

        Returns:
            Updated item document dict or None if not found.
        """
        try:
            if not ObjectId.is_valid(item_id):
                logger.warning(f"Invalid ObjectId received: {item_id}")
            updated_data={**data,"updated_at":datetime.utcnow()}
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(item_id), "list_id": list_id, "is_deleted": False},
                {"$set": updated_data},
                return_document=ReturnDocument.AFTER,
            )
            if result:
                return _to_response(result)
            logger.info(f"Shopping item not found. item_id={item_id}")
        except Exception:
            logger.exception(f"Failed to update shopping item. item_id={item_id}")
            return None

    async def soft_delete(self, list_id: str, item_id: str) -> bool:
        """
        Soft-delete a shopping item by setting is_deleted=True.

        Args:
            list_id: The parent shopping list ID.
            item_id: The string ObjectId of the item.

        Returns:
            True if deleted, False if not found.
        """
        try:
            if not ObjectId.is_valid(item_id):
                logger.warning(
                    f"Invalid ObjectId received: {item_id}"
                )
                return False

            result = await self.collection.update_one(
                {
                    "_id": ObjectId(item_id),
                    "list_id": list_id,
                    "is_deleted": False,
                },
                {
                    "$set": {
                        "is_deleted": True,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            if result.modified_count == 0:
                logger.info(
                    f"Shopping item not found for deletion. item_id={item_id}"
                )
                return False

            return True
        except Exception:
            logger.exception(f"Failed to delete shopping item. item_id={item_id}")
            return False

    async def mark_all_purchased(self, list_id: str) -> int:
        """
        Mark all non-deleted items in a list as purchased.

        Args:
            list_id: The parent shopping list ID.

        Returns:
            Number of items updated.
        """
        result = await self.collection.update_many(
            {"list_id": list_id, "is_deleted": False},
            {"$set": {"purchased": True, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count

    async def delete_by_list_id(self, list_id: str) -> int:
        """
        Soft-delete all items belonging to a list (used when deleting a list).

        Args:
            list_id: The parent shopping list ID.

        Returns:
            Number of items soft-deleted.
        """
        result = await self.collection.update_many(
            {"list_id": list_id, "is_deleted": False},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count
