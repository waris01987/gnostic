from typing import List, Type, Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic import BaseModel

from ..config.pg_database import get_db
from app.repositories.base import BaseRepository
from app.common.errors import RecordNotExistsError, RecordAlreadyExistsError


class BaseService:
    def __init__(
        self,
        db: Session = Depends(get_db),
        repository: Type[BaseRepository] = None,
        response: Type[BaseModel] = None,
    ):
        """
        Initialize with database session and repository.
        """
        self.db = db
        if repository is None:
            raise ValueError("Repository cannot be None")
        self.repository = repository
        self.response = response

    async def create(self, payload: BaseModel, **filters):
        """
        Create a new instance with validation to ensure it doesn't already exist.
        """
        # Check if the object already exists by filtering with unique fields (e.g., email or name)
        existing_instance = await self.repository.get_one(
            self.db, **filters
        )  # Adjust field as necessary
        if existing_instance:
            raise RecordAlreadyExistsError

        # Proceed with creation if no existing object is found
        instance = self.repository.ModelClass(**payload.dict())
        created_instance = await self.repository.create(self.db, instance)
        return self.response.from_orm(created_instance)

    async def update(self, payload: BaseModel, **filters):
        """
        Update instance with validation to ensure the object exists.
        """
        obj = await self.repository.get_one(self.db, **filters)
        if not obj:
            raise RecordNotExistsError
        # Proceed with updating the object
        await self.repository.update_all(self.db, data=payload.dict(), **filters)
        updated_instance = await self.repository.get_one(self.db, **filters)
        return self.response.from_orm(updated_instance)

    async def delete(self, **filters):
        """
        Delete an instance with validation to ensure the object exists.
        """
        obj = await self.repository.get_one(self.db, **filters)
        if not obj:
            raise RecordNotExistsError

        # Proceed with deletion
        return await self.repository.delete(self.db, obj)

    async def get_one(self, **filters) -> Optional[BaseModel]:
        """
        Retrieve and validate a single instance by filters.
        """
        instance = await self.repository.get_one(self.db, **filters)
        if not instance:
            raise RecordNotExistsError

        return self.response.from_orm(instance)

    async def get_all(self) -> List[BaseModel]:
        """
        Retrieve all instances from the repository.
        """
        instances = await self.repository.get_all(self.db)
        return [self.response.from_orm(instance) for instance in instances]
