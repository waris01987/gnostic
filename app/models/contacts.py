from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel, Base


ContactGroups = Table(
    "contact_groups",
    Base.metadata,
    Column(
        "contact_id", UUID(as_uuid=True), ForeignKey("contacts.uuid"), primary_key=True
    ),
    Column("group_id", UUID(as_uuid=True), ForeignKey("groups.uuid"), primary_key=True),
)


class Group(BaseModel):
    __tablename__ = "groups"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), unique=True)
    description = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    additional_details = Column(JSON, default={})

    contacts = relationship("Contact", secondary=ContactGroups, back_populates="groups")
    owner = relationship("User")


class Contact(BaseModel):
    __tablename__ = "contacts"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(50))
    first_name = Column(String(100))
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100))
    country = Column(String(100))
    country_of_stay = Column(String(100))
    personal_email = Column(String(255), unique=True, index=True)
    personal_mobile = Column(String(50))
    birthday = Column(DateTime)
    bio = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    additional_details = Column(JSON, default={})

    social_accounts = relationship(
        "SocialAccounts",
        back_populates="contact",
        uselist=False,
        cascade="all, delete-orphan",
    )
    meeting_info = relationship(
        "MeetingInfo",
        back_populates="contact",
        uselist=False,
        cascade="all, delete-orphan",
    )
    additional_information = relationship(
        "AdditionalInformation",
        back_populates="contact",
        uselist=False,
        cascade="all, delete-orphan",
    )
    groups = relationship("Group", secondary=ContactGroups, back_populates="contacts")
    owner = relationship("User")


class SocialAccounts(BaseModel):
    __tablename__ = "social_accounts"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.uuid"))
    personal_website = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    facebook = Column(String(255), nullable=True)
    instagram = Column(String(255), nullable=True)
    google = Column(String(255), nullable=True)
    skype = Column(String(255), nullable=True)
    zoom = Column(String(255), nullable=True)
    google_meet = Column(String(255), nullable=True)
    viber = Column(String(255), nullable=True)
    whatsapp = Column(String(255), nullable=True)
    x = Column(String(255), nullable=True)
    additional_details = Column(JSON, default={})

    contact = relationship("Contact", back_populates="social_accounts")


class MeetingInfo(BaseModel):
    __tablename__ = "meeting_info"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.uuid"))
    place = Column(String(255))
    mean = Column(String(50))
    date = Column(DateTime)
    google_link = Column(String(255), nullable=True)
    comments = Column(Text, nullable=True)
    additional_details = Column(JSON, default={})

    contact = relationship("Contact", back_populates="meeting_info")


class AdditionalInformation(BaseModel):
    __tablename__ = "additional_information"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.uuid"))
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    related_person = Column(String(255), nullable=True)
    who_introduced = Column(String(255), nullable=True)
    additional_details = Column(JSON, default={})

    contact = relationship("Contact", back_populates="additional_information")
