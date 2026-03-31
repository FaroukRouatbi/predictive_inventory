from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class InventoryBase(BaseModel):
    quantity_on_hand: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    location: Optional[str] = None

class InventoryCreate(InventoryBase):
    product_id: UUID = Field(..., description="The UUID of the linked product")


class InventoryUpdate(BaseModel):
    quantity_on_hand: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    location: Optional[str] = None

class InventoryResponse(InventoryBase):
    id: UUID
    product_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Required for SQLAlchemy compatibility
    model_config = ConfigDict(from_attributes=True)