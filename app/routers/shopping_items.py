"""
Router for Shopping Item CRUD endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.database.mongodb import get_database
from app.services.shopping_item_service import ShoppingItemService
from app.schemas.shopping_item import (
    ShoppingItemCreate,
    ShoppingItemUpdate,
    ShoppingItemResponse,
    BulkItemCreate,
    PaginatedShoppingItemResponse,
)

router = APIRouter(prefix="/shopping-lists/{list_id}/items", tags=["Shopping Items"])


def get_service(db=Depends(get_database)) -> ShoppingItemService:
    """Dependency: instantiate ShoppingItemService with DB."""
    return ShoppingItemService(db)


@router.post(
    "",
    summary="Add item to shopping list",
    description="Adds a new item to the specified shopping list.",
    response_model=ShoppingItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    list_id: str,
    data: ShoppingItemCreate,
    service: ShoppingItemService = Depends(get_service),
):
    """
    Add a new item to a shopping list.

    Args:
        list_id: The parent shopping list ID.
        data: Item creation payload.
        service: Injected ShoppingItemService.

    Returns:
        Newly created item document.
    """
    return await service.create_item(list_id, data)


@router.post(
    "/bulk",
    summary="Bulk add items to shopping list",
    description="Adds multiple items to the specified shopping list in one request.",
    response_model=List[ShoppingItemResponse],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_items(
    list_id: str,
    data: BulkItemCreate,
    service: ShoppingItemService = Depends(get_service),
):
    """
    Bulk add items to a shopping list.

    Args:
        list_id: The parent shopping list ID.
        data: Bulk item creation payload.
        service: Injected ShoppingItemService.

    Returns:
        List of created item documents.
    """
    return await service.bulk_create_items(list_id, data.items)


@router.get(
    "",
    summary="Get all items in a shopping list",
    description="Retrieves all items in the specified shopping list with optional name search and pagination.",
    response_model=PaginatedShoppingItemResponse,
)
async def list_items(
    list_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page"),
    search: Optional[str] = Query(None, description="Search items by name"),
    service: ShoppingItemService = Depends(get_service),
):
    """
    Get all items in a shopping list.

    Args:
        list_id: The parent shopping list ID.
        page: Page number (1-based).
        page_size: Results per page.
        search: Optional item name filter.
        service: Injected ShoppingItemService.

    Returns:
        Paginated list of shopping items.
    """
    items, total = await service.get_all_items(list_id=list_id, page=page, page_size=page_size, search=search)
    return PaginatedShoppingItemResponse(total=total, page=page, page_size=page_size, items=items)


@router.get(
    "/{item_id}",
    summary="Get a shopping item",
    description="Retrieves a single item from the specified shopping list by item ID.",
    response_model=ShoppingItemResponse,
)
async def get_item(
    list_id: str,
    item_id: str,
    service: ShoppingItemService = Depends(get_service),
):
    """
    Get a specific item from a shopping list.

    Args:
        list_id: The parent shopping list ID.
        item_id: The item ObjectId string.
        service: Injected ShoppingItemService.

    Returns:
        Shopping item document.
    """
    return await service.get_item(list_id, item_id)


@router.put(
    "/{item_id}",
    summary="Update a shopping item",
    description="Updates one or more fields of the specified shopping item.",
    response_model=ShoppingItemResponse,
)
async def update_item(
    list_id: str,
    item_id: str,
    data: ShoppingItemUpdate,
    service: ShoppingItemService = Depends(get_service),
):
    """
    Update a shopping item.

    Args:
        list_id: The parent shopping list ID.
        item_id: The item ObjectId string.
        data: Fields to update.
        service: Injected ShoppingItemService.

    Returns:
        Updated shopping item document.
    """
    return await service.update_item(list_id, item_id, data)


@router.delete(
    "/{item_id}",
    summary="Delete a shopping item",
    description="Soft-deletes the specified shopping item.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_item(
    list_id: str,
    item_id: str,
    service: ShoppingItemService = Depends(get_service),
):
    """
    Delete a shopping item (soft delete).

    Args:
        list_id: The parent shopping list ID.
        item_id: The item ObjectId string.
        service: Injected ShoppingItemService.
    """
    await service.delete_item(list_id, item_id)


@router.patch(
    "/mark-all-purchased",
    summary="Mark all items as purchased",
    description="Marks every non-deleted item in the specified shopping list as purchased.",
)
async def mark_all_purchased(
    list_id: str,
    service: ShoppingItemService = Depends(get_service),
):
    """
    Mark all items in a shopping list as purchased.

    Args:
        list_id: The parent shopping list ID.
        service: Injected ShoppingItemService.

    Returns:
        Count of updated items.
    """
    return await service.mark_all_purchased(list_id)
