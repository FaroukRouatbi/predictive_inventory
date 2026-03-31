from app.models.enums import Currency
from app.models.enums import ProductCategory
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    sku: str = Field(..., min_length=3)
    name: str
    description: str
    category: ProductCategory
    price_cents: int = Field(gt=0)
    currency: Currency

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ProductCategory] = None
    price_cents: Optional[int] = Field(default=None, gt=0)
    currency: Optional[Currency] = None

class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


    model_config = ConfigDict(from_attributes=True)