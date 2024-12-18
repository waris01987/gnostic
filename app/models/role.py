import uuid
from sqlalchemy import String, Table, Column, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    permissions = relationship(
        "Permission", secondary="role_permissions", back_populates="roles"
    )


class RolePermission(BaseModel):
    __tablename__ = "role_permissions"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.uuid"))
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.uuid"))
