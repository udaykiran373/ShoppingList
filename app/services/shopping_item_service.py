"""
Service layer for Shopping Item business logic.
"""

from typing import List, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, status

from app.repositories.shopping_item_repository import ShoppingItemRepository
from app.repositories.shopping_list_repository import ShoppingListRepository
from app.schemas.shopping_item import ShoppingItemCreate, ShoppingItemUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ShoppingItemService:
    """Orchestrates business logic for shopping item operations."""

    def __init__(self, db):
        self.repo = ShoppingItemRepository(db)
        self.list_repo = ShoppingListRepository(db)

    async def _assert_list_exists(self, list_id: str) -> None:
        """Raise 404 if the parent shopping list does not exist."""
        doc = await self.list_repo.get_by_id(list_id)
        if not doc:
            logger.error(f"Shopping list not found. list_id={list_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Shopping list not found", "error_code": "SHOPPING_LIST_NOT_FOUND"},
            )

    async def create_item(self, list_id: str, data: ShoppingItemCreate) -> dict:
        """
        Add a new item to a shopping list.

        Args:
            list_id: The parent shopping list ID.
            data: Item creation payload.

        Returns:
            Newly created shopping item document.
        """
        await self._assert_list_exists(list_id)
        doc = {
            "name": data.name,
            "quantity": data.quantity,
            "unit": data.unit,
            "purchased": data.purchased,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await self.repo.create(list_id, doc)
        logger.info(f"Item created successfully. list_id={list_id} item_id={result['id']}")
        return result

    async def bulk_create_items(self, list_id: str, items: List[ShoppingItemCreate]) -> List[dict]:
        """
        Add multiple items to a shopping list at once.

        Args:
            list_id: The parent shopping list ID.
            items: List of item creation payloads.

        Returns:
            List of created item documents.
        """
        await self._assert_list_exists(list_id)
        docs = [
            {
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "purchased": item.purchased,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            for item in items
        ]
        results = await self.repo.bulk_create(list_id, docs)
        logger.info(f"Bulk items created. list_id={list_id} count={len(results)}")
        return results

    async def get_all_items(
        self,
        list_id: str,
        page: int,
        page_size: int,
        search: Optional[str],
    ) -> Tuple[List[dict], int]:
        """
        Get all items for a shopping list with pagination and optional search.

        Args:
            list_id: The parent shopping list ID.
            page: Page number (1-based).
            page_size: Results per page.
            search: Optional item name search query.

        Returns:
            Tuple of (list of item dicts, total count).
        """
        await self._assert_list_exists(list_id)
        return await self.repo.get_all(list_id=list_id, page=page, page_size=page_size, search=search)

    async def get_item(self, list_id: str, item_id: str) -> dict:
        """
        Retrieve a single item by list and item ID or raise 404.

        Args:
            list_id: The parent shopping list ID.
            item_id: The item ObjectId string.

        Returns:
            Item document.

        Raises:
            HTTPException: 404 if not found.
        """
        await self._assert_list_exists(list_id)
        doc = await self.repo.get_by_id(list_id, item_id)
        if not doc:
            logger.error(f"Item not found. list_id={list_id} item_id={item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Item not found", "error_code": "ITEM_NOT_FOUND"},
            )
        return doc

    async def update_item(self, list_id: str, item_id: str, data: ShoppingItemUpdate) -> dict:
        """
        Update a shopping item's fields.

        Args:
            list_id: The parent shopping list ID.
            item_id: The item ObjectId string.
            data: Fields to update.

        Returns:
            Updated item document.

        Raises:
            HTTPException: 400 if no fields provided, 404 if not found.
        """
        updates = data.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "No fields provided for update", "error_code": "NO_UPDATE_FIELDS"},
            )
        await self._assert_list_exists(list_id)
        result = await self.repo.update(list_id, item_id, updates)
        if not result:
            logger.error(f"Item not found for update. list_id={list_id} item_id={item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Item not found", "error_code": "ITEM_NOT_FOUND"},
            )
        logger.info(f"Item updated successfully. list_id={list_id} item_id={item_id}")
        return result

    async def delete_item(self, list_id: str, item_id: str) -> None:
        """
        Soft-delete a shopping item.

        Args:
            list_id: The parent shopping list ID.
            item_id: The item ObjectId string.

        Raises:
            HTTPException: 404 if not found.
        """
        await self._assert_list_exists(list_id)
        deleted = await self.repo.soft_delete(list_id, item_id)
        if not deleted:
            logger.error(f"Item not found for deletion. list_id={list_id} item_id={item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Item not found", "error_code": "ITEM_NOT_FOUND"},
            )
        logger.info(f"Item deleted successfully. list_id={list_id} item_id={item_id}")

    async def mark_all_purchased(self, list_id: str) -> dict:
        """
        Mark all items in a list as purchased.

        Args:
            list_id: The parent shopping list ID.

        Returns:
            Dict with count of updated items.
        """
        await self._assert_list_exists(list_id)
        count = await self.repo.mark_all_purchased(list_id)
        logger.info(f"Marked {count} items as purchased. list_id={list_id}")
        return {"updated": count}
