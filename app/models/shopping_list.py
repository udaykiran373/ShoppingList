"""
MongoDB document model for Shopping List.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ShoppingListDocument(BaseModel):
    """Represents a shopping list document stored in MongoDB."""

    id: Optional[str] = None
    name: str
    description: Optional[str] = ""
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
