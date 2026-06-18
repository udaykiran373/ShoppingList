"""
Pydantic schemas for Shopping List request validation and API responses.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ShoppingListCreate(BaseModel):
    """Payload for creating a new shopping list."""

    name: str = Field(..., min_length=3, max_length=100, description="Name of the shopping list")
    description: Optional[str] = Field("", max_length=500, description="Optional description")

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank")
        return v.strip()


class ShoppingListUpdate(BaseModel):
    """Payload for updating an existing shopping list."""

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Name must not be blank")
        return v.strip() if v else v


class ShoppingListResponse(BaseModel):
    """Response schema for a shopping list."""

    id: str
    name: str
    description: Optional[str] = ""
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedShoppingListResponse(BaseModel):
    """Paginated response for shopping lists."""

    total: int
    page: int
    page_size: int
    items: List[ShoppingListResponse]
