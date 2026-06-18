"""
Router for Shopping List CRUD endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.database.mongodb import get_database
from app.services.shopping_list_service import ShoppingListService
from app.schemas.shopping_list import (
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingListResponse,
    PaginatedShoppingListResponse,
)

router = APIRouter(prefix="/shopping-lists", tags=["Shopping Lists"])


def get_service(db=Depends(get_database)) -> ShoppingListService:
    """Dependency: instantiate ShoppingListService with DB."""
    return ShoppingListService(db)


@router.post(
    "",
    summary="Create a shopping list",
    description="Creates a new shopping list and persists it in MongoDB.",
    response_model=ShoppingListResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_shopping_list(
    data: ShoppingListCreate,
    service: ShoppingListService = Depends(get_service),
):
    """
    Create a new shopping list.

    Args:
        data: Shopping list creation payload.
        service: Injected ShoppingListService.

    Returns:
        Newly created shopping list.
    """
    return await service.create_shopping_list(data)


@router.get(
    "",
    summary="List all shopping lists",
    description="Retrieves all shopping lists with optional name search and pagination.",
    response_model=PaginatedShoppingListResponse,
)
async def list_shopping_lists(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page"),
    search: Optional[str] = Query(None, description="Search by name"),
    service: ShoppingListService = Depends(get_service),
):
    """
    Get all shopping lists.

    Args:
        page: Page number (1-based).
        page_size: Number of results per page.
        search: Optional name filter.
        service: Injected ShoppingListService.

    Returns:
        Paginated list of shopping lists.
    """
    items, total = await service.get_all_shopping_lists(page=page, page_size=page_size, search=search)
    return PaginatedShoppingListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get(
    "/{list_id}",
    summary="Get a shopping list",
    description="Retrieves a single shopping list by its ID.",
    response_model=ShoppingListResponse,
)
async def get_shopping_list(
    list_id: str,
    service: ShoppingListService = Depends(get_service),
):
    """
    Get a shopping list by ID.

    Args:
        list_id: The ObjectId string of the shopping list.
        service: Injected ShoppingListService.

    Returns:
        Shopping list document.
    """
    return await service.get_shopping_list(list_id)


@router.put(
    "/{list_id}",
    summary="Update a shopping list",
    description="Updates the name and/or description of an existing shopping list.",
    response_model=ShoppingListResponse,
)
async def update_shopping_list(
    list_id: str,
    data: ShoppingListUpdate,
    service: ShoppingListService = Depends(get_service),
):
    """
    Update a shopping list.

    Args:
        list_id: The ObjectId string of the shopping list.
        data: Fields to update.
        service: Injected ShoppingListService.

    Returns:
        Updated shopping list document.
    """
    return await service.update_shopping_list(list_id, data)


@router.delete(
    "/{list_id}",
    summary="Delete a shopping list",
    description="Soft-deletes a shopping list and all its items.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_shopping_list(
    list_id: str,
    service: ShoppingListService = Depends(get_service),
):
    """
    Delete a shopping list (soft delete).

    Args:
        list_id: The ObjectId string of the shopping list.
        service: Injected ShoppingListService.
    """
    await service.delete_shopping_list(list_id)
