from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class ReorderAlertResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity_on_hand: int
    reorder_level: int
    recommended_reorder_quantity: int
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResolveAlertRequest(BaseModel):
    notes: Optional[str] = None