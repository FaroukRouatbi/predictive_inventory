from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.models.base import Base
from app.models.mixins import TimeStampMixins


class ReorderAlert(TimeStampMixins, Base):
    __tablename__ = "reorder_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Snapshot of stock levels at time of alert
    quantity_on_hand = Column(Integer, nullable=False)
    reorder_level = Column(Integer, nullable=False)
    recommended_reorder_quantity = Column(Integer, nullable=False)

    # Alert lifecycle
    is_resolved = Column(Boolean, nullable=False, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)

    # Relationship
    product = relationship("Product", backref="reorder_alerts")
