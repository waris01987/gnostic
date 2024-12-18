from typing import Optional
from pydantic import BaseModel, EmailStr, Field, SecretStr, constr, ConfigDict, field_validator

from app.common.enums import UserType, Gender


class IndividualRegistration(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    organisation_name: Optional[str] = Field(None, max_length=100)
    email: EmailStr = Field(..., max_length=254)
    gender: int = Field(...)
    date_of_birth: Optional[str] = Field(None)
    country_code: str = Field(..., max_length=5)
    country_code_str: Optional[str] = Field(None)
    cell_phone_number_1: str = Field(..., max_length=15)
    password: str = Field(..., min_length=8, max_length=20)

    @field_validator("email")
    @classmethod
    def email_must_be_lowercase(cls, v):
        return v.lower()


class OrganisationRegistration(BaseModel):
    organisation_name: str = Field(..., max_length=100)
    ceo_first_name: str = Field(..., max_length=100)
    ceo_last_name: str = Field(..., max_length=100)
    email: EmailStr = Field(..., max_length=254)
    established_year: int = Field(..., gt=1800, lt=2100)
    country: str = Field(..., max_length=100)
    no_of_employee: Optional[constr(pattern=r"^\[\d+,\d*\]$")] = Field(None)
    website_link: Optional[str] = Field(None, max_length=255)
    linkedin: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=8, max_length=20)

    @field_validator("email")
    @classmethod
    def email_must_be_lowercase(cls, v):
        return v.lower()


class Login(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    password: SecretStr

    @field_validator("email")
    @classmethod
    def email_must_be_lowercase(cls, v):
        return v.lower()


class AccessJWT(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RequestResetPassword(BaseModel):
    email: EmailStr = Field(..., max_length=254)

    @field_validator("email")
    @classmethod
    def email_must_be_lowercase(cls, v):
        return v.lower()


class ResetPassword(BaseModel):
    token: str
    new_password: SecretStr


class OTPResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: SecretStr

    @field_validator("email")
    @classmethod
    def email_must_be_lowercase(cls, v):
        return v.lower()


class ChangePassword(BaseModel):
    current_password: SecretStr
    new_password: SecretStr


class OAuthCallbackPayload(BaseModel):
    code: str
    provider: str
    redirect_uri: str
    user_type: UserType
    gender: Gender
    code_verifier: Optional[str] = None
    platform: Optional[str] = "web"


class TokenRefreshRequest(BaseModel):
    refresh_token: str
    access_token: str
    user_type: Optional[int]


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="New access token.")
    refresh_token: str = Field(..., description="New refresh token.")
    token_type: str = Field("bearer", description="Token type, usually 'bearer'.")


# ============================ [Response Models] ======================================
class IndividualRegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    first_name: str
    last_name: str
    organisation_name: Optional[str]
    email: EmailStr
    cell_phone_number_1: str
    gender: Optional[int]
    date_of_birth: Optional[str]
    country_code: str
    country_code_str: Optional[str]

    @classmethod
    def from_orm(cls, user_orm):
        return cls(
            uuid=str(user_orm.uuid),
            first_name=user_orm.first_name,
            last_name=user_orm.last_name,
            organisation_name=user_orm.organisation_name,
            email=user_orm.email,
            cell_phone_number_1=user_orm.cell_phone_number_1,
            gender=user_orm.gender,
            date_of_birth=user_orm.date_of_birth,
            country_code=user_orm.country_code,
            country_code_str=user_orm.country_code_str,
        )


class OrganisationRegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    organisation_name: str
    ceo_first_name: str
    ceo_last_name: str
    email: EmailStr
    established_year: int

    @classmethod
    def from_orm(cls, org_orm):
        return cls(
            uuid=str(org_orm.uuid),
            organisation_name=org_orm.organisation_name,
            ceo_first_name=org_orm.ceo_first_name,
            ceo_last_name=org_orm.ceo_last_name,
            email=org_orm.email,
            established_year=org_orm.established_year,
        )
