from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.models.base import Base
from app.models.mixins import TimeStampMixins


class User(TimeStampMixins, Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)