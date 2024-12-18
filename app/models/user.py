# User model defining the structure for user data in the database.
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel
from app.models.language import UserLanguage


class User(BaseModel):
    __tablename__ = "users"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    title = Column(String, nullable=True)
    organisation_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    user_type = Column(Integer, nullable=False)
    gender = Column(Integer, nullable=False)
    date_of_birth = Column(TIMESTAMP(timezone=True), nullable=True)
    country_code = Column(String, nullable=True)
    country_code_str = Column(String, nullable=True)
    cell_phone_number_1 = Column(String, nullable=True)
    cell_phone_number_2 = Column(String, nullable=True)
    landline = Column(String, nullable=True)
    password = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    address = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.uuid"))
    role = relationship("Role")
    languages = relationship("UserLanguage", back_populates="user")

    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, unique=True, nullable=True)
    oauth_details = Column(JSON, nullable=True)
    profile_picture = Column(String, nullable=True)
    oauth_email = Column(String, index=True, nullable=True)


# class Address(BaseModel):
#     __tablename__ = 'addresses'
#
#     id = Column(Integer, primary_key=True, index=True)
#     street_address = Column(String(255), nullable=False)
#     street_address2 = Column(String(255), nullable=True)  # Optional
#     city = Column(String(100), nullable=False)
#     state = Column(String(100), nullable=False)
#     postal_code = Column(String(20), nullable=False)
#     country = Column(String(100), nullable=False)
#
#     latitude = Column(String(50), nullable=True)  # Coordinates if required
#     longitude = Column(String(50), nullable=True)
#
#     user_id = Column(Integer, ForeignKey('users.id'))
#     user = relationship('User', back_populates='addresses')
#
#     def __repr__(self):
#         return f"<Address(id={self.id}, street_address={self.street_address}, city={self.city}, state={self.state}, country={self.country})>"
