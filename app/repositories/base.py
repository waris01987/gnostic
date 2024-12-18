from pydantic import BaseModel
from sqlalchemy.sql import exists, text
from sqlalchemy import asc, desc, or_, text, update, delete, select
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Optional, Type, Tuple
from sqlalchemy.sql.expression import func
from math import ceil

from sqlalchemy.testing.util import total_size

from app.schemas.pagination import PaginationDetails
from ..config.pg_database import get_db


class BaseRepository:
    # model: Type[BaseModel] = None
    ModelClass = BaseModel

    @staticmethod
    def get_db():
        return next(get_db())

    @classmethod
    async def exists(cls, db: Session, **kwargs) -> bool:
        try:
            query = select(
                exists().where(
                    *[
                        getattr(cls.ModelClass, key) == value
                        for key, value in kwargs.items()
                    ]
                )
            )
            result = db.execute(query)
            return result.scalar()
        finally:
            db.close()

    @staticmethod
    async def create(db: Session, instance: BaseModel):
        try:
            db.add(instance)
            db.commit()
            db.refresh(instance)
            return instance
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @classmethod
    async def get_one(
        cls, db: Session, options: List = None, include_role: bool = False, **kwargs
    ) -> Optional[BaseModel]:
        try:
            query = select(cls.ModelClass)
            if include_role:
                query = query.options(joinedload(cls.ModelClass.role))
            if options:
                query = query.options(*options)
            if kwargs:
                query = query.filter_by(**kwargs)
            result = db.execute(query)
            return result.scalars().one_or_none()
        finally:
            db.close()

    @classmethod
    async def get_all(
        cls,
        db: Session,
        include_role: bool = False,
        order_by: Optional[List[Tuple[str, bool]]] = None,
        search: Optional[str] = None,
        search_columns: Optional[List[str]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        **kwargs,
    ) -> List[BaseModel]:
        try:
            query = select(cls.ModelClass)
            if include_role:
                query = query.options(joinedload(cls.ModelClass.role))

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
            return result.scalars().all()
        finally:
            db.close()

    @classmethod
    async def get_paginated(
            cls,
            db: Session,
            page: Optional[int] = None,
            page_size: Optional[int] = None,
            include_role: bool = False,
            order_by: Optional[List[Tuple[str, bool]]] = None,
            search: Optional[str] = None,
            search_columns: Optional[List[str]] = None,
            **kwargs,
    ):
        """
        Retrieve paginated data with metadata.

        Args:
            db (Session): Database session.
            page (Optional[int]): Current page number.
            page_size (Optional[int]): Number of records per page.
            include_role (bool): Whether to include related roles.
            order_by (Optional[List[Tuple[str, bool]]]): Columns for sorting.
            search (Optional[str]): Search term.
            search_columns (Optional[List[str]]): Columns to search in.
            **kwargs: Additional filters.

        Returns:
            Tuple[List, PaginationDetails]: Paginated data with metadata.
        """
        query = select(cls.ModelClass)

        if include_role:
            query = query.options(joinedload(cls.ModelClass.role))

        # Apply filters from kwargs
        if kwargs:
            query = query.filter_by(**kwargs)

        # Apply search conditions
        if search and search_columns:
            conditions = [text(f"{col} ILIKE :search") for col in search_columns]
            query = query.filter(or_(*conditions)).params(search=f"%{search}%")

        # Apply ordering
        if order_by:
            order_clauses = []
            for column_name, is_descending in order_by:
                column = getattr(cls.ModelClass, column_name, None)
                if column is not None:
                    order_clauses.append(desc(column) if is_descending else asc(column))
                else:
                    raise ValueError(f"Invalid column name '{column_name}' for sorting")
            query = query.order_by(*order_clauses)

        result = db.execute(query)
        data = result.scalars().all()

        if page is None or page_size is None:
            pagination_details = PaginationDetails(
                current_page=1,
                page_size=len(data),
                total_records=len(data),
                total_pages=1,
            )
            return data, pagination_details

        # Get total count
        # total_count_query = select(func.count()).select_from(cls.ModelClass)
        # total_count_result = db.execute(total_count_query)
        # total_count = total_count_result.scalar()

        total_count = len(data)
        total_pages = ceil(total_count / page_size) if total_count > 0 else 1

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Fetch paginated results
        result = db.execute(query)
        data = result.scalars().all()

        pagination_details = PaginationDetails(
            current_page=page,
            page_size=page_size,
            total_records=total_count,
            total_pages=total_pages,
        )
        return data, pagination_details


    @classmethod
    async def update_all(cls, db: Session, data: Dict[str, any], **kwargs):
        try:
            query = update(cls.ModelClass).values(data)
            if kwargs:
                query = query.filter_by(**kwargs)
            db.execute(query)
            db.commit()
        finally:
            db.close()

    @classmethod
    async def delete(cls, db: Session, instance: BaseModel):
        try:
            db.delete(instance)
            db.commit()
        finally:
            db.close()

    @classmethod
    async def delete_all(cls, db: Session, **kwargs):
        try:
            query = delete(cls.ModelClass)
            if kwargs:
                query = query.filter_by(**kwargs)
            db.execute(query)
            db.commit()
        finally:
            db.close()
