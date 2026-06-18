"""
Pydantic schemas for Shopping Item request validation and API responses.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ShoppingItemCreate(BaseModel):
    """Payload for adding a new item to a shopping list."""

    name: str = Field(..., min_length=1, max_length=200, description="Name of the item")
    quantity: float = Field(..., gt=0, description="Quantity (must be > 0)")
    unit: str = Field(..., min_length=1, max_length=50, description="Unit of measurement")
    purchased: bool = Field(False, description="Whether item has been purchased")

    @field_validator("name", "unit")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be blank")
        return v.strip()


class ShoppingItemUpdate(BaseModel):
    """Payload for updating an existing shopping item."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    purchased: Optional[bool] = None

    @field_validator("name", "unit")
    @classmethod
    def must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Field must not be blank")
        return v.strip() if v else v


class ShoppingItemResponse(BaseModel):
    """Response schema for a shopping item."""

    id: str
    list_id: str
    name: str
    quantity: float
    unit: str
    purchased: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BulkItemCreate(BaseModel):
    """Payload for bulk item creation."""

    items: List[ShoppingItemCreate] = Field(..., min_length=1)


class PaginatedShoppingItemResponse(BaseModel):
    """Paginated response for shopping items."""

    total: int
    page: int
    page_size: int
    items: List[ShoppingItemResponse]
