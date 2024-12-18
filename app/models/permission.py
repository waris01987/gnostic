import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class Permission(BaseModel):
    __tablename__ = "permissions"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    scope = Column(String, nullable=False)
    roles = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )
