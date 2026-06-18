"""
MongoDB document model for Shopping Item.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ShoppingItemDocument(BaseModel):
    """Represents a shopping item document stored in MongoDB."""

    id: Optional[str] = None
    list_id: str
    name: str
    quantity: float
    unit: str
    purchased: bool = False
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
