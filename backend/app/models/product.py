from app.models.enums import Currency
from app.models.enums import ProductCategory
from app.models.mixins import TimeStampMixins
from uuid import uuid4
from sqlalchemy import Column, Text, String, Integer, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import UUID


class Product(TimeStampMixins, Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    sku = Column(String, nullable=False, unique=True, index=True)

    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(Enum(ProductCategory), nullable=False, index=True)

    price_cents = Column(Integer, nullable=False)

    currency = Column(Enum(Currency), nullable=False, default=Currency.USD)

    inventory_item = relationship(
        "InventoryItem",
        back_populates="product",
        uselist=False
    )