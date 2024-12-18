from uuid import UUID
from typing import List, Optional
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload, Session

from .base import BaseRepository
from app.models.role import Role, RolePermission
from app.models.user import User
from app.models.permission import Permission


class PermissionRepository(BaseRepository):
    ModelClass = Permission

    @classmethod
    async def get_permissions_with_roles(cls, **kwargs):
        db = cls.get_db()
        try:
            query = select(cls.ModelClass).options(joinedload(cls.ModelClass.roles))
            if kwargs:
                query = query.filter_by(**kwargs)
            result = db.execute(query)
            return result.unique().scalars().all()
        finally:
            db.close()

    @classmethod
    async def get_permission_with_roles(cls, **kwargs):
        db = cls.get_db()
        try:
            query = select(cls.ModelClass).options(joinedload(cls.ModelClass.roles))
            if kwargs:
                query = query.filter_by(**kwargs)
            result = db.execute(query)
            return result.unique().scalars().one_or_none()
        finally:
            db.close()

    @classmethod
    async def get_roles_by_uuid_list(
        cls, db: Session, uuid_list: List[UUID]
    ) -> List[Role]:
        query = select(Role).where(Role.uuid.in_(uuid_list))
        result = db.execute(query).scalars()
        return list(result)

    @classmethod
    async def save_permission(cls, db: Session, permission: Permission):
        try:
            merged_permission = db.merge(permission)
            db.commit()
            db.refresh(merged_permission)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @classmethod
    async def get_user_role(cls, db: Session, user_id: str):
        """Fetch the user's role from the database using role_id in User table."""
        try:
            query = (
                select(Role.name)
                .join(User, Role.uuid == User.role_id)
                .where(User.uuid == user_id)
            )
            result = db.execute(query).scalars().first()
            return result if result else None
        except Exception as e:
            db.rollback()
            raise e

    @classmethod
    async def get_permissions_by_role(cls, db: Session, role_name: str) -> List[str]:
        """Fetch permissions associated with a given role."""
        try:
            query = (
                select(Permission.name)
                .join(RolePermission)
                .join(Role)
                .filter(Role.name == role_name)
            )
            result = db.execute(query).scalars().all()
            return result
        except Exception as e:
            db.rollback()
            raise e
