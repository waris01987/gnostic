import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID, INT4RANGE

from .base import BaseModel


class Organisation(BaseModel):
    __tablename__ = "organisations"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_name = Column(String, nullable=False)
    ceo_first_name = Column(String, nullable=False)
    ceo_last_name = Column(String, nullable=False)
    linkedin = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    established_year = Column(Integer, nullable=False)
    country = Column(String, nullable=False)
    no_of_employee = Column(INT4RANGE, nullable=False)
    website_link = Column(String, nullable=True)
    password = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
