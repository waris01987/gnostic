from typing import List

from app.common.enums import UserType
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.repositories.permission import PermissionRepository
from app.models.permission import Permission
from app.schemas.permission import (
    UpdatePermission,
    PermissionResponse,
    CreatePermission,
    PermissionRolesResponse,
    BulkAssignRoles,
    DeletePermissionResponse
)
from app.common.errors import RecordNotExistsError, RecordAlreadyExistsError
from ..config.pg_database import get_db
from ..config.settings import ORGANISATION_ROLE
from ..schemas.pagination import PaginatedResponse


class PermissionService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def create_permission(self, payload: CreatePermission):
        existing_permission = await PermissionRepository.exists(
            self.db, name=payload.name
        )
        if existing_permission:
            raise RecordAlreadyExistsError(
                message="Permission with provided name already exist"
            )

        # existing_role = await RoleRepository.exists(self.db, uuid=payload.role_id)
        # if not existing_role:
        #     raise RecordNotExistsError(message="Roles doesn't exist")

        permission = Permission(
            name=payload.name,
            description=payload.description,
            scope=payload.scope,
            # role_id=payload.role_id
        )
        await PermissionRepository.create(self.db, instance=permission)
        return PermissionResponse.from_orm(permission)

    async def get_all_permissions(self, search_str: str = None, page: int = None, page_size: int = None):
        permissions, pagination_details = await PermissionRepository.get_paginated(
            self.db,
            order_by=[('created_at', True)],
            search=search_str,
            search_columns=['name', 'description'],
            page=page,
            page_size=page_size
        )
        if not permissions:
            raise RecordNotExistsError

        return PaginatedResponse(
            data=[PermissionResponse.from_orm(permission) for permission in permissions],
            pagination=pagination_details
        )

    async def update_permission(self, permission_id: str, payload: UpdatePermission):
        permission = await PermissionRepository.get_one(self.db, uuid=permission_id)
        if not permission:
            raise RecordNotExistsError

        update_data = {
            "name": payload.name if payload.name else permission.name,
            "scope": payload.scope if payload.scope else permission.scope,
            "description": (
                payload.description if payload.description else permission.description
            ),
        }

        await PermissionRepository.update_all(
            self.db, data=update_data, uuid=permission_id
        )
        permission_obj = await PermissionRepository.get_permission_with_roles(uuid=permission_id)
        return PermissionRolesResponse.from_orm(permission_obj).dict()

    async def delete_permission(self, permission_id: str):
        permission = await PermissionRepository.get_one(self.db, uuid=permission_id)
        if not permission:
            raise RecordNotExistsError(f"Permission with ID {permission_id} not found.")

        await PermissionRepository.delete(self.db, instance=permission)
        return DeletePermissionResponse.from_orm(permission)

    @staticmethod
    async def get_permission_roles():
        permissions = await PermissionRepository.get_permissions_with_roles()
        if not permissions:
            raise RecordNotExistsError
        return [
            PermissionRolesResponse.from_orm(permission) for permission in permissions
        ]

    async def bulk_assign_roles(self, payload: List[BulkAssignRoles]):
        response_data = []
        for update in payload:
            permission = await PermissionRepository.get_permission_with_roles(
                uuid=update.permission_id
            )
            if not permission:
                continue

            permission = self.db.merge(permission)
            if update.roles_to_add:
                roles_to_add = await PermissionRepository.get_roles_by_uuid_list(
                    self.db, update.roles_to_add
                )
                for role in roles_to_add:
                    if role not in permission.roles:
                        permission.roles.append(role)

            if update.roles_to_remove:
                roles_to_remove = await PermissionRepository.get_roles_by_uuid_list(
                    self.db, update.roles_to_remove
                )
                for role in roles_to_remove:
                    if role in permission.roles:
                        permission.roles.remove(role)

            await PermissionRepository.save_permission(self.db, permission)
            response_data.append(PermissionRolesResponse.from_orm(permission))
        return response_data

    async def get_user_permissions(self, entity_id: str, entity_type: int) -> List[str]:
        if entity_type == UserType.INDIVIDUAL_USER.value:
            role = await PermissionRepository.get_user_role(self.db, entity_id)
        elif entity_type == UserType.ORGANISATION.value:
            role = ORGANISATION_ROLE
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload."
            )
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User role not found."
            )
        permission_names = await PermissionRepository.get_permissions_by_role(
            self.db, role
        )
        return permission_names
