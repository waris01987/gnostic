from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Optional, List

from app.common.utils import format_timestamp
from app.schemas.role import RoleResponse


class CreatePermission(BaseModel):
    name: str = Field(..., max_length=100)
    scope: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=254)
    # role_id: UUID = Field(...)


class UpdatePermission(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    scope: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=254)


# ============================ [RolePermission] ======================================
class BulkAssignRoles(BaseModel):
    permission_id: UUID
    roles_to_add: Optional[List[UUID]] = []  # Roles to add to the permission
    roles_to_remove: Optional[List[UUID]] = []


# ============================ [Response Models] ======================================
class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    name: str
    scope: str
    description: Optional[str]
    created_at: str

    @classmethod
    def from_orm(cls, permission_orm):
        return cls(
            uuid=str(permission_orm.uuid),
            name=permission_orm.name,
            scope=permission_orm.scope,
            created_at=format_timestamp(permission_orm.created_at),
            description=permission_orm.description,
        )


class PermissionRolesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    name: str
    scope: str
    description: Optional[str]
    created_at: str
    roles: List[RoleResponse]

    @classmethod
    def from_orm(cls, permission_orm):
        return cls(
            uuid=str(permission_orm.uuid),
            name=permission_orm.name,
            scope=permission_orm.scope,
            description=permission_orm.description,
            created_at=format_timestamp(permission_orm.created_at),
            roles=[RoleResponse.from_orm(role) for role in permission_orm.roles],
        )


class DeletePermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str

    @classmethod
    def from_orm(cls, permission_orm):
        return cls(
            uuid=str(permission_orm.uuid),
        )
