from uuid import uuid4
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.mixins import TimeStampMixins

class InventoryItem(TimeStampMixins, Base):
    __tablename__ = "inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    quantity_on_hand = Column(Integer, nullable=False, default=0)
    
    reorder_level = Column(Integer, nullable=False, default=10)
    location = Column(String, nullable=True) 

    product = relationship("Product", back_populates="inventory_item")