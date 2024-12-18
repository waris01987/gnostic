from app.models.user import User
from .base import BaseRepository
from app.models.role import Role, RolePermission
from pydantic import BaseModel
from sqlalchemy import asc, desc, func, or_, text, select
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Type, Tuple


class RoleRepository(BaseRepository):
    ModelClass = Role

    @classmethod
    async def get_all_with_user_count(
        cls,
        db: Session,
        order_by: Optional[List[Tuple[str, bool]]] = None,
        search: Optional[str] = None,
        search_columns: Optional[List[str]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **kwargs,
    ) -> List[Tuple[BaseModel, int]]:
        try:
            query = (
                select(
                    cls.ModelClass,
                    func.count(User.uuid).label("user_count"),
                    func.array_agg(func.coalesce(User.profile_picture, "")).label(
                        "profile_pictures"
                    ),
                )
                .outerjoin(User, cls.ModelClass.uuid == User.role_id)
                .group_by(cls.ModelClass.uuid)
            )

            if kwargs:
                query = query.filter_by(**kwargs)

            if search and search_columns:
                conditions = [text(f"{col} ILIKE :search") for col in search_columns]
                query = query.filter(or_(*conditions)).params(search=f"%{search}%")

            if order_by:
                order_clauses = []
                for column_name, is_descending in order_by:
                    column = getattr(cls.ModelClass, column_name, None)
                    if column is not None:
                        order_clauses.append(
                            desc(column) if is_descending else asc(column)
                        )
                    else:
                        raise ValueError(
                            f"Invalid column name '{column_name}' for sorting"
                        )
                query = query.order_by(*order_clauses)

            if page and page_size:
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)

            result = db.execute(query)
            return [
                (role, user_count, profile_pictures or [])
                for role, user_count, profile_pictures in result
            ]
        finally:
            db.close()

class RolePermissionRepository(BaseRepository):
    ModelClass = RolePermission
