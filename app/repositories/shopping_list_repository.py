"""
Repository layer for Shopping List MongoDB operations.
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
        try:
            document={
                **data,
                "is_deleted":False
            }
        
            result = await self.collection.insert_one(document)
            doc = await self.collection.find_one({"_id": result.inserted_id})
            if doc:
                return _to_response(doc)
                
            logger.error(f"Inserted shopping list could not be retrieved. id={result.inserted_id}"
)
            return None
        except Exception as e:
            logger.exception(f"Failed to create shopping list {str(e)}")
            return None

    async def get_all(
        self,
        page: int,
        page_size: int,
        search: Optional[str] = None,
    ) -> Tuple[List[dict], int]:
        """
        Retrieve all non-deleted shopping lists with optional name search and pagination.

        """
        try:
            query: dict = {"is_deleted": False}
            if search:
                search.strip()
            if search:
                query["$text"] = {"$search": search}

            total = await self.collection.count_documents(query)
            skip = (page - 1) * page_size
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            docs = [_to_response(doc) async for doc in cursor]
            return docs, total
        except Exception:
            logger.exception("Failed to retrieve shopping lists")
            return [], 0

    async def get_by_id(self, list_id: str) -> Optional[dict]:
        """
        Retrieve a single non-deleted shopping list by ID.

        Args:
            list_id: The string ObjectId of the list.

        Returns:
            Document dict or None if not found.
        """
        try:
            if not ObjectId.is_valid(list_id):
                logger.warning(f"Invalid ObjectId recieved :{list_id}")
                return None
            doc = await self.collection.find_one({"_id": ObjectId(list_id), "is_deleted": False})
            if doc:
                return _to_response(doc)
            logger.info(f"shopping list not found {list_id}")
            return None

        except Exception as e:
            logger.exception(f"Failed to retrieve shopping list {str(e)}")
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
            if not ObjectId.is_valid(list_id):
                logger.warning(f"invalid ObjectId recieved : {list_id}")
                return None
            update_data={**data,"updated_at":datetime.utcnow()}
            result=await self.collection.find_one_and_update(
                {"_id":ObjectId(list_id),"is_deleted":False},
                {"$set":update_data},
                return_document=ReturnDocument.After
            )
            if result:
                return _to_response(result)
            logger.info(f"shopping list not found : {list_id}")
            return None
        except Exception as e:
            logger.error(f"database error {str(e)}")
            return None
        

    async def soft_delete(self, list_id: str) -> bool:
        """
        Soft-delete a shopping list by setting is_deleted=True.

        Args:
            list_id: The string ObjectId of the list.

        Returns:
            True if deleted, False if not found.
        """
        try:
            if not ObjectId.is_valid(list_id):
                logger.info(f"invalid objectid received:{list_id}")

            result = await self.collection.update_one(
                {"_id": ObjectId(list_id), "is_deleted": False},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            if result.modified_count==0:
                logger.info(f"shoppinglist not found for deletion {list_id}")
                return False
            return True
        except Exception as e:
            logger.exception(f"Failed to delete shoppinglist {list_id}")
            return False
