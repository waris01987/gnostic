from typing import List

from app.repositories.user import UserRepository
from fastapi import Depends
from sqlalchemy.orm import Session

from app.schemas.role import CreateRole, UpdateRole, RoleResponse, UsersRoleResponse, DeleteRoleResponse
from app.schemas.pagination import PaginatedResponse
from app.repositories.role import RoleRepository, RolePermissionRepository
from app.common.errors import (
    RecordAlreadyExistsError,
    RecordNotExistsError,
    RoleAssignedToUserError, RoleAssignedToPermissionError
)
from app.models.role import Role
from ..config.pg_database import get_db


class RoleService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def create_role(self, payload: CreateRole):
        existing_role = await RoleRepository.exists(self.db, name=payload.name)
        if existing_role:
            raise RecordAlreadyExistsError

        role = Role(name=payload.name, description=payload.description)
        await RoleRepository.create(self.db, instance=role)
        return RoleResponse.from_orm(role)


    async def get_all_roles(self, search_str: str = None, page: int = None, page_size: int = None) -> PaginatedResponse:
        roles, pagination_details = await RoleRepository.get_paginated(
            self.db,
            order_by=[('created_at', True)],
            search=search_str,
            search_columns=['name', 'description'],
            page=page,
            page_size=page_size
        )

        return PaginatedResponse(
            data=[RoleResponse.from_orm(role) for role in roles],
            pagination=pagination_details
        )

    async def get_roles_user_count(self, request) -> List[UsersRoleResponse]:
        users_role = await RoleRepository.get_all_with_user_count(self.db)
        if not users_role:
            raise RecordNotExistsError
        return [
            UsersRoleResponse.from_orm(
                role, request=request, user_count=count, profile_picture=profile_picture
            )
            for role, count, profile_picture in users_role
        ]

    # async def get_all_users_with_role(self, search_str: str = None, page: int = None, page_size: int = None) -> List[RoleResponse]:
    #     roles = await RoleRepository.get_all(
    #         self.db,
    #         order_by=[('created_at', True)],
    #         search=search_str,
    #         search_columns=['name', 'description'],
    #         page=page,
    #         page_size=page_size
    #     )
    #     if not roles:
    #         raise RecordNotExistsError
    #     return [RoleResponse.from_orm(role) for role in roles]


    async def update_role(self, role_id: str, payload: UpdateRole):
        role = await RoleRepository.get_one(self.db, uuid=role_id)
        if not role:
            raise RecordNotExistsError

        update_data = {
            "name": payload.name if payload.name else role.name,
            "description": (
                payload.description if payload.description else role.description
            ),
        }

        await RoleRepository.update_all(self.db, data=update_data, uuid=role_id)
        updated_role = await RoleRepository.get_one(self.db, uuid=role_id)
        return RoleResponse.from_orm(updated_role)

    async def delete_role(self, role_id: str):
        role = await RoleRepository.get_one(self.db, uuid=role_id)
        if not role:
            raise RecordNotExistsError

        assigned_roles = await UserRepository.exists(self.db, role_id=role_id)
        if assigned_roles:
            raise RoleAssignedToUserError

        assigned_roles = await RolePermissionRepository.exists(self.db, role_id=role_id)
        if assigned_roles:
            raise RoleAssignedToPermissionError

        await RoleRepository.delete(self.db, instance=role)
        return DeleteRoleResponse.from_orm(role)
