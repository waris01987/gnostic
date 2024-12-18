from app.common.enums import UserType
from fastapi import Request
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, constr, ConfigDict
from sqlalchemy.dialects.postgresql import Range

from app.common.utils import format_timestamp


class UpdateOrganisation(BaseModel):
    organisation_name: Optional[str] = Field(None, max_length=100)
    ceo_first_name: Optional[str] = Field(None, max_length=100)
    ceo_last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=254)
    established_year: Optional[int] = Field(None, gt=1800, lt=2100)
    country: Optional[str] = Field(None, max_length=100)
    no_of_employee: Optional[constr(pattern=r"^\[\d+,\d*\]$")] = Field(None)
    website_link: Optional[str] = Field(None, max_length=255)
    linkedin: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=20)


class GetOrganisationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    organisation_name: str
    ceo_first_name: str
    ceo_last_name: str
    email: EmailStr
    user_type: int
    established_year: int
    country: str
    no_of_employee: Any
    website_link: str
    linkedin: str
    profile_picture: Optional[str]
    created_at: Optional[str]

    @classmethod
    def from_orm(cls, request: Request, org_orm):
        no_of_employee_value = org_orm.no_of_employee
        if no_of_employee_value and isinstance(org_orm.no_of_employee, Range):
            if org_orm.no_of_employee.upper:
                no_of_employee_value = [
                    org_orm.no_of_employee.lower,
                    org_orm.no_of_employee.upper - 1,
                ]
            else:
                no_of_employee_value = [org_orm.no_of_employee.lower, None]

        profile_picture = None
        if org_orm.profile_picture:
            profile_picture = f"{request.base_url}{org_orm.profile_picture}"

        return cls(
            uuid=str(org_orm.uuid),
            organisation_name=org_orm.organisation_name,
            ceo_first_name=org_orm.ceo_first_name,
            ceo_last_name=org_orm.ceo_last_name,
            email=org_orm.email,
            user_type=UserType.ORGANISATION.value,
            established_year=org_orm.established_year,
            country=org_orm.country,
            no_of_employee=no_of_employee_value,
            website_link=org_orm.website_link,
            linkedin=org_orm.linkedin,
            profile_picture=profile_picture,
            created_at=format_timestamp(org_orm.created_at),
        )
