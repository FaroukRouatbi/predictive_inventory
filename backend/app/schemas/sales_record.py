from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class SalesRecordBase(BaseModel):
    quantity_sold: int = Field(..., gt=0)
    price_at_sale: int = Field(..., gt=0)


class SalesRecordCreate(SalesRecordBase):
    product_id: UUID
    inventory_id: UUID
    sold_at: Optional[datetime] = None


class SalesRecordResponse(SalesRecordBase):
    id: UUID
    product_id: UUID
    inventory_id: UUID
    sold_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)