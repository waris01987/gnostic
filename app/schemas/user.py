# User-related schemas for data validation and serialization.
from fastapi import Request
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.common.utils import format_timestamp


class UpdateIndividualUser(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    organisation_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=254)
    gender: Optional[int] = Field(None)
    date_of_birth: Optional[str] = Field(None)
    country_code: Optional[str] = Field(None, max_length=5)
    cell_phone_number_1: Optional[str] = Field(None, max_length=15)
    bio: Optional[str] = Field(None)
    password: Optional[str] = Field(None, min_length=8, max_length=20)
    address: Optional[str] = Field(None, max_length=254)
    languages: Optional[List[str]] = Field(None)
    country_code_str: Optional[str] = Field(None, max_length=2)


class GetIndividualUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    first_name: str
    last_name: str
    organisation_name: Optional[str]
    email: Optional[EmailStr | None]
    country_code: Optional[str | None]
    cell_phone_number_1: Optional[str | None]
    gender: int
    user_type: Optional[int]
    date_of_birth: Optional[str | None]
    created_at: Optional[str]
    bio: Optional[str]
    profile_picture: Optional[str]
    address: Optional[str]
    country_code_str: Optional[str]
    designation: Optional[str]
    languages: Optional[List[dict]]

    @classmethod
    def from_orm(
        cls, user_orm, request: Request, language_names: Optional[List[dict]] = None
    ):
        date_of_birth = user_orm.date_of_birth
        if isinstance(date_of_birth, date):
            date_of_birth = date_of_birth.isoformat()

        profile_picture = None
        if user_orm.profile_picture:
            profile_picture = f"{request.base_url}{user_orm.profile_picture}"

        return cls(
            uuid=str(user_orm.uuid),
            first_name=user_orm.first_name,
            last_name=user_orm.last_name,
            organisation_name=user_orm.organisation_name,
            email=user_orm.email,
            country_code=user_orm.country_code,
            cell_phone_number_1=user_orm.cell_phone_number_1,
            gender=user_orm.gender,
            user_type=user_orm.user_type,
            date_of_birth=date_of_birth,
            created_at=format_timestamp(user_orm.created_at),
            bio=user_orm.bio,
            profile_picture=profile_picture,
            address=user_orm.address,
            country_code_str=user_orm.country_code_str,
            designation=user_orm.designation,
            languages=language_names,
        )


class GetUserRolesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    first_name: str
    last_name: str
    organisation_name: Optional[str]
    email: Optional[EmailStr | None]
    cell_phone_number_1: Optional[str | None]
    user_type: Optional[int]
    date_of_birth: Optional[str | None]
    created_at: Optional[str]
    profile_picture: Optional[str]
    designation: Optional[str]
    role_name: Optional[str]

    @classmethod
    def from_orm(cls, user_orm, request: Request):
        date_of_birth = user_orm.date_of_birth
        if isinstance(date_of_birth, date):
            date_of_birth = date_of_birth.isoformat()

        profile_picture = None
        if user_orm.profile_picture:
            profile_picture = f"{request.base_url}{user_orm.profile_picture}"

        return cls(
            uuid=str(user_orm.uuid),
            first_name=user_orm.first_name,
            last_name=user_orm.last_name,
            organisation_name=user_orm.organisation_name,
            email=user_orm.email,
            cell_phone_number_1=user_orm.cell_phone_number_1,
            user_type=user_orm.user_type,
            date_of_birth=date_of_birth,
            created_at=format_timestamp(user_orm.created_at),
            bio=user_orm.bio,
            profile_picture=profile_picture,
            designation=user_orm.designation,
            role_name=user_orm.role.name if user_orm.role else None,
        )
