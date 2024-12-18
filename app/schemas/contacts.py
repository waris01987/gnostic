from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from uuid import UUID


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    additional_details: Dict = Field(default_factory=dict)


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SocialAccountsCreate(BaseModel):
    personal_website: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    facebook: Optional[HttpUrl] = None
    instagram: Optional[str] = None
    google: Optional[HttpUrl] = None
    skype: Optional[str] = None
    zoom: Optional[str] = None
    google_meet: Optional[str] = None
    viber: Optional[str] = None
    whatsapp: Optional[str] = None
    x: Optional[str] = None
    additional_details: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class MeetingInfoCreate(BaseModel):
    place: str
    mean: str
    date: datetime
    google_link: Optional[str] = None
    comments: Optional[str] = None
    additional_details: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class AdditionalInformationCreate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    related_person: Optional[str] = None
    who_introduced: Optional[str] = None
    additional_details: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    title: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    country: str
    country_of_stay: str
    personal_email: EmailStr
    personal_mobile: str
    birthday: datetime
    bio: Optional[str] = None
    group_ids: List[int] = Field(default_factory=list)
    social_accounts: SocialAccountsCreate
    meeting_info: MeetingInfoCreate
    additional_information: AdditionalInformationCreate
    additional_details: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class SocialAccountsResponse(BaseModel):
    uuid: UUID
    personal_website: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    facebook: Optional[HttpUrl] = None
    instagram: Optional[str] = None
    google: Optional[HttpUrl] = None
    skype: Optional[str] = None
    zoom: Optional[str] = None
    google_meet: Optional[str] = None
    viber: Optional[str] = None
    whatsapp: Optional[str] = None
    x: Optional[str] = None
    additional_details: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class MeetingInfoResponse(BaseModel):
    uuid: UUID
    place: str
    mean: str
    date: datetime
    google_link: Optional[str] = None
    comments: Optional[str] = None
    additional_details: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class AdditionalInformationResponse(BaseModel):
    uuid: UUID
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    related_person: Optional[str] = None
    who_introduced: Optional[str] = None
    additional_details: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class ContactResponse(BaseModel):
    uuid: UUID
    title: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    country: str
    country_of_stay: str
    personal_email: EmailStr
    personal_mobile: str
    birthday: datetime
    bio: Optional[str] = None
    group_ids: List[int] = Field(default_factory=list)
    social_accounts: SocialAccountsResponse
    meeting_info: MeetingInfoResponse
    additional_information: AdditionalInformationResponse
    additional_details: Dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SocialAccountsUpdate(BaseModel):
    personal_website: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    facebook: Optional[HttpUrl] = None
    instagram: Optional[str] = None
    google: Optional[HttpUrl] = None
    skype: Optional[str] = None
    zoom: Optional[str] = None
    google_meet: Optional[str] = None
    viber: Optional[str] = None
    whatsapp: Optional[str] = None
    x: Optional[str] = None
    additional_details: Optional[Dict] = Field(default_factory=dict)


class MeetingInfoUpdate(BaseModel):
    place: Optional[str] = None
    mean: Optional[str] = None
    date: Optional[datetime] = None
    google_link: Optional[str] = None
    comments: Optional[str] = None
    additional_details: Optional[Dict] = Field(default_factory=dict)


class AdditionalInformationUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    related_person: Optional[str] = None
    who_introduced: Optional[str] = None
    additional_details: Optional[Dict] = Field(default_factory=dict)


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_email: Optional[EmailStr] = None
    personal_mobile: Optional[str] = None
    bio: Optional[str] = None
    group_ids: Optional[List[int]] = Field(default_factory=list)
    social_accounts: Optional[SocialAccountsUpdate] = None
    meeting_info: Optional[MeetingInfoUpdate] = None
    additional_information: Optional[AdditionalInformationUpdate] = None
    additional_details: Optional[Dict] = Field(default_factory=dict)

    class Config:
        from_attributes = True
