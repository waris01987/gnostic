import uuid
from .base import BaseRepository
from app.models.user import User
from sqlalchemy.sql import select  # type: ignore
from typing import Optional


class UserRepository(BaseRepository):
    ModelClass = User

    @classmethod
    async def get_by_user_id(cls, user_id: uuid) -> Optional[User]:
        db = cls.get_db()
        try:
            query = select(cls.ModelClass).filter_by(uuid=user_id)
            result = db.execute(query)
            return result.scalars().one_or_none()
        finally:
            db.close()

    @classmethod
    async def get_by_oauth_id_and_provider(
        cls, oauth_id: str, oauth_provider: str
    ) -> Optional[User]:
        db = cls.get_db()
        try:
            query = select(cls.ModelClass).filter_by(
                oauth_id=oauth_id, oauth_provider=oauth_provider
            )
            result = db.execute(query)
            return result.scalars().one_or_none()
        finally:
            db.close()

    @classmethod
    async def update(cls, user_id: uuid, data: dict) -> Optional[User]:
        db = cls.get_db()
        try:
            # Find the user
            query = select(cls.ModelClass).filter_by(uuid=user_id)
            result = db.execute(query)
            user = result.scalars().one_or_none()

            if user:
                # Update fields
                for key, value in data.items():
                    setattr(user, key, value)

                # Commit and refresh
                db.commit()
                db.refresh(user)
                return user
            else:
                return None
        finally:
            db.close()
