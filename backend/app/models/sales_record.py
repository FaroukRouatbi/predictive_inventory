from sqlalchemy import Column, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.models.base import Base
from app.models.mixins import TimeStampMixins


class SalesRecord(TimeStampMixins, Base):
    __tablename__ = "sales_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    inventory_id = Column(
        UUID(as_uuid=True),
        ForeignKey("inventory_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Sale Data
    quantity_sold = Column(Integer, nullable=False)
    price_at_sale = Column(Integer, nullable=False)  # cents, snapshot at time of sale

    # Business timestamp — separate from created_at (record-keeping) in the mixin
    sold_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relationships (read-only, for joins in forecasting queries)
    product = relationship("Product", backref="sales_records")
    inventory = relationship("InventoryItem", backref="sales_records")

    # Composite index — every forecasting query filters by product + time window
    __table_args__ = (
        Index("ix_sales_records_product_sold_at", "product_id", "sold_at"),
    )