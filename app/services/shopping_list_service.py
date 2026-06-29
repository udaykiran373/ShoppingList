"""
Service layer for Shopping List business logic.
"""

from typing import Optional, Tuple, List
from datetime import datetime
from fastapi import HTTPException, status

from app.repositories.shopping_list_repository import ShoppingListRepository
from app.repositories.shopping_item_repository import ShoppingItemRepository
from app.schemas.shopping_list import ShoppingListCreate, ShoppingListUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ShoppingListService:
    """Orchestrates business logic for shopping list operations."""

    def __init__(self, db):
        self.repo = ShoppingListRepository(db)
        self.item_repo = ShoppingItemRepository(db)

    async def create_shopping_list(self, data: ShoppingListCreate) -> dict:
        """
        Create a new shopping list.

        Args:
            data: Shopping list creation payload.

        Returns:
            Newly created shopping list document.
        """
        doc = {
            "name": data.name,
            "description": data.description or "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await self.repo.create(doc)
        if result is None:
            logger.error("Failed to create shopping list.")
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                      "message": "Failed to create shopping list",
                      "error_code": "SHOPPING_LIST_CREATE_FAILED"
                    }
            )
        logger.info(f"shopping list created succesfully list_id={result['id']}")
        return result

    async def get_all_shopping_lists(
        self,
        page: int,
        page_size: int,
        search: Optional[str],
    ) -> Tuple[List[dict], int]:
        """
        Retrieve all shopping lists with pagination and optional search.

        Args:
            page: Page number (1-based).
            page_size: Results per page.
            search: Optional name search query.

        Returns:
            Tuple of (list of shopping list dicts, total count).
        """
        if search:
            search = search.strip()
        return await self.repo.get_all(page=page, page_size=page_size, search=search)

    async def get_shopping_list(self, list_id: str) -> dict:
        """
        Retrieve a shopping list by ID or raise 404.

        Args:
            list_id: The shopping list ObjectId string.

        Returns:
            Shopping list document.

        Raises:
            HTTPException: 404 if not found.
        """
        doc = await self.repo.get_by_id(list_id)

        if doc:
             return doc

        logger.info(f"Shopping list not found. list_id={list_id}")
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail={
              "message": "Shopping list not found",
              "error_code": "SHOPPING_LIST_NOT_FOUND"
            },
        )

    async def update_shopping_list(self, list_id: str, data: ShoppingListUpdate) -> dict:
        """
        Update a shopping list's fields.

        Args:
            list_id: The shopping list ObjectId string.
            data: Fields to update.

        Returns:
            Updated shopping list document.

        Raises:
            HTTPException: 404 if not found, 400 if no fields provided.
        """
        updates = data.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "No fields provided for update", "error_code": "NO_UPDATE_FIELDS"},
            )
        result = await self.repo.update(list_id, updates)
        if not result:
            logger.info(f"Shopping list not found for update. list_id={list_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Shopping list not found", "error_code": "SHOPPING_LIST_NOT_FOUND"},
            )
        logger.info(f"Shopping list updated successfully. list_id={list_id}")
        return result

    async def delete_shopping_list(self, list_id: str) -> None:
        """
        Soft-delete a shopping list and all its items.

        Args:
            list_id: The shopping list ObjectId string.

        Raises:
            HTTPException: 404 if not found.
        """
        deleted = await self.repo.soft_delete(list_id)
        if not deleted:
            logger.info(f"Shopping list not found for deletion. list_id={list_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Shopping list not found", "error_code": "SHOPPING_LIST_NOT_FOUND"},
            )
        await self.item_repo.delete_by_list_id(list_id)
        logger.info(f"Shopping list deleted successfully. list_id={list_id}")
