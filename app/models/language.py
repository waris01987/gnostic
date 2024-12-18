# User model defining the structure for user data in the database.
import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class Language(BaseModel):
    __tablename__ = "languages"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)


class UserLanguage(BaseModel):
    __tablename__ = "user_languages"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    language_id = Column(
        UUID(as_uuid=True), ForeignKey("languages.uuid"), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="languages")
    language = relationship("Language")
