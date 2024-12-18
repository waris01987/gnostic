import uuid

import bcrypt
import httpx
import json
import base64
import pyotp
from validators import url

from app.repositories.role import RoleRepository
from fastapi import Depends, Request
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import SecretStr, EmailStr
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.dialects.postgresql.ranges import Range

from app.config import settings
from app.schemas.auth import (
    IndividualRegistration,
    OrganisationRegistration,
    Login,
    AccessJWT,
    IndividualRegistrationResponse,
    OrganisationRegistrationResponse,
    OAuthCallbackPayload,
    TokenRefreshRequest,
    ChangePassword,
    OTPResetPassword,
)
from app.schemas.organisation import GetOrganisationResponse
from app.schemas.user import GetIndividualUserResponse
from app.models.organisation import Organisation
from app.repositories.user import UserRepository
from app.repositories.organisation import OrganisationRepository
from app.common.errors import (
    UserAlreadyExistsError,
    OrganisationAlreadyExistsError,
    AuthenticationFailedError,
    RecordNotExistsError,
    InvalidTokenError,
    InvalidProviderError,
    InvalidOTPError,
    UserNotFoundError,
)
from app.models.user import User
from app.models.role import Role
from app.models.language import UserLanguage
from app.common.enums import UserType, OAuthProvider
from app.services.email import EmailService
from app.config.settings import (
    GOOGLE_WEB_CLIENT_ID,
    GOOGLE_IOS_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    INSTAGRAM_CLIENT_ID,
    INSTAGRAM_CLIENT_SECRET,
    FACEBOOK_CLIENT_ID,
    FACEBOOK_CLIENT_SECRET,
    YAHOO_CLIENT_ID,
    YAHOO_CLIENT_SECRET,
    TWITTER_CLIENT_ID,
    TWITTER_CLIENT_SECRET,
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
    APPLE_CLIENT_ID,
    APPLE_CLIENT_SECRET,
    OTP_SECRET_KEY,
    OTP_EXPIRE_SECONDS,
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
)
from app.api.response import APIResponse

from google.oauth2 import id_token
from google.auth.transport import requests
import requests as req

from ..common.context import UserContext
from ..config.pg_database import get_db
from ..models.base import BaseModel


class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def individual_registration(
        self, payload: IndividualRegistration
    ) -> IndividualRegistrationResponse:
        existing_user = await UserRepository.exists(
            self.db, email=payload.email
        ) or await UserRepository.exists(
            self.db, cell_phone_number_1=payload.cell_phone_number_1
        )
        if existing_user:
            raise UserAlreadyExistsError(
                message="User already exists with this email or phone number"
            )

        if await OrganisationRepository.exists(self.db, email=payload.email):
            raise UserAlreadyExistsError(
                message="Organisation already exists with this email"
            )

        role_obj = await RoleRepository.get_one(self.db, name="Individual-User")
        if not role_obj:
            role_obj = Role(name="Individual-User", description="Individual")
            print(f"role_obj: {role_obj}")
            role_obj = await RoleRepository.create(self.db, role_obj)

        user = User(
            uuid=uuid.uuid4(),
            first_name=payload.first_name,
            last_name=payload.last_name,
            organisation_name=payload.organisation_name,
            email=payload.email,
            gender=payload.gender,
            role_id=role_obj.uuid,
            date_of_birth=payload.date_of_birth,
            password=self.hash_password(password=payload.password),
            user_type=UserType.INDIVIDUAL_USER.value,
            country_code=payload.country_code,
            country_code_str=payload.country_code_str,
            cell_phone_number_1=payload.cell_phone_number_1,
        )
        await UserRepository.create(self.db, instance=user)
        return IndividualRegistrationResponse.from_orm(user)

    async def register_organisation(
        self, payload: OrganisationRegistration
    ) -> OrganisationRegistrationResponse:
        existing_organisation = await OrganisationRepository.get_one(
            self.db, email=payload.email
        )
        if existing_organisation:
            raise OrganisationAlreadyExistsError

        if await UserRepository.exists(self.db, email=payload.email):
            raise UserAlreadyExistsError(message="User already exists with this email")

        min_count, max_count = payload.no_of_employee.strip("[]").split(",")
        min_count = int(min_count)
        max_count = None if max_count == "" else int(max_count)

        if max_count is None:
            no_of_employee_range = f"[{min_count},)"
        else:
            no_of_employee_range = f"[{min_count},{max_count}]"
        organisation = Organisation(
            uuid=uuid.uuid4(),
            organisation_name=payload.organisation_name,
            ceo_first_name=payload.ceo_first_name,
            ceo_last_name=payload.ceo_last_name,
            email=payload.email,
            established_year=payload.established_year,
            country=payload.country,
            no_of_employee=no_of_employee_range,
            website_link=payload.website_link,
            linkedin=payload.linkedin,
            password=self.hash_password(payload.password),
        )

        await OrganisationRepository.create(self.db, instance=organisation)
        return OrganisationRegistrationResponse.from_orm(organisation)

    async def login(self, request: Request, payload: Login) -> AccessJWT:
        user = await UserRepository.get_one(self.db, email=payload.email)
        if not user:
            user = await OrganisationRepository.get_one(self.db, email=payload.email)
            if not user:
                raise AuthenticationFailedError

        self.validate_user_and_password(user=user, password=payload.password)
        return self.create_tokens(request=request, user=user, otp_validated=False)

    async def change_password(self, payload: ChangePassword):
        current_user_email = UserContext.get().get("email")
        if not current_user_email:
            raise AuthenticationFailedError

        user = await UserRepository.get_one(
            self.db, email=current_user_email
        ) or await OrganisationRepository.get_one(self.db, email=current_user_email)
        if not user:
            raise UserNotFoundError

        self.validate_user_and_password(user=user, password=payload.current_password)
        hashed_password = self.hash_password(payload.new_password.get_secret_value())
        repository = (
            UserRepository if isinstance(user, User) else OrganisationRepository
        )
        await repository.update_all(
            self.db, {"password": hashed_password}, uuid=user.uuid
        )

    async def get_profile_details(self, request):
        current_user_email = UserContext.get().get("email")
        user_type = UserContext.get().get("user_type")
        if not current_user_email or not user_type:
            raise AuthenticationFailedError

        if user_type == UserType.INDIVIDUAL_USER.value:
            user = await UserRepository.get_one(
                self.db,
                email=current_user_email,
                options=[
                    selectinload(User.languages).selectinload(UserLanguage.language)
                ],
            )
            if user:
                language_names = [
                    {"code": language.language.code, "name": language.language.name}
                    for language in user.languages
                ]
                return GetIndividualUserResponse.from_orm(
                    user, request, language_names=language_names
                )
        else:
            user = await OrganisationRepository.get_one(
                self.db, email=current_user_email
            )
            return GetOrganisationResponse.from_orm(request, user)

    @staticmethod
    def validate_user_and_password(user: BaseModel, password: SecretStr):
        raw_password = password.get_secret_value()
        # if not bcrypt.verify(raw_password, user.password):
        #     raise AuthenticationFailedError
        if not bcrypt.checkpw(
            raw_password.encode("utf-8"), user.password.encode("utf-8")
        ):
            raise AuthenticationFailedError

    async def handle_token_refresh(
        self, token_request: TokenRefreshRequest
    ) -> AccessJWT:
        try:
            try:
                refresh_token_payload = self.decode_jwt(token_request.refresh_token)
                refresh_token_valid = self.is_token_valid(
                    refresh_token_payload, "refresh"
                )

                if not refresh_token_valid:
                    raise InvalidTokenError("Refresh token is expired or invalid.")
                user = await self.get_user_from_token(
                    refresh_token_payload, user_type=token_request.user_type
                )

            except ExpiredSignatureError:
                return await self.generate_new_tokens(
                    token_request.refresh_token, token_request.user_type
                )

            try:
                access_token_payload = self.decode_jwt(token_request.access_token)
                access_token_valid = self.is_token_valid(access_token_payload, "access")

                if access_token_valid:
                    return AccessJWT(
                        access_token=token_request.access_token,
                        refresh_token=token_request.refresh_token,
                        token_type="bearer",
                    )

            except ExpiredSignatureError:
                user = await self.get_user_from_token(
                    refresh_token_payload, int(token_request.user_type)
                )
                new_access_token = self.generate_payload(user, otp_validated=False)
                return AccessJWT(
                    access_token=new_access_token,
                    refresh_token=token_request.refresh_token,
                    token_type=settings.JWT_TYPE,
                )

        except JWTError as e:
            raise InvalidTokenError("Invalid token.")

        return await self.generate_new_tokens(
            token_request.refresh_token, token_request.user_type
        )

    async def generate_new_tokens(
        self, refresh_token: str, user_type: int
    ) -> AccessJWT:
        user = await self.get_user_from_token(self.decode_jwt(refresh_token))
        new_access_token = self.generate_payload(user, otp_validated=False)
        new_refresh_token = self.create_refresh_jwt(
            {"sub": str(user.uuid), "type": "refresh"}
        )

        return AccessJWT(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    @staticmethod
    def is_token_valid(payload: Dict[str, Any], token_type: str) -> bool:
        try:
            if "type" in payload and payload["type"] != token_type:
                return False

            exp = datetime.fromtimestamp(payload["exp"])
            current_time = datetime.utcnow()
            return current_time < exp

        except (KeyError, ValueError) as e:
            return False

    async def get_user_from_token(
        self, payload: Dict[str, Any], user_type: int
    ) -> User:
        user_id = payload.get("sub")
        if user_type == UserType.INDIVIDUAL_USER.value:
            user = await UserRepository.get_one(self.db, uuid=user_id)
            if not user:
                raise RecordNotExistsError("User not found.")
            return user
        elif user_type == UserType.ORGANISATION.value:
            org = await OrganisationRepository.get_one(self.db, uuid=user_id)
            if not org:
                raise RecordNotExistsError("Organisation not found.")
            return org

    def generate_payload(self, user: BaseModel, otp_validated: bool) -> Dict[str, Any]:
        """Generate payload for access token."""
        base_payload = {
            "otp_validated": otp_validated,
            "iat": datetime.utcnow(),
        }

        if isinstance(user, Organisation):
            no_of_employee_value = user.no_of_employee
            if isinstance(no_of_employee_value, Range):
                no_of_employee_value = [
                    no_of_employee_value.lower,
                    no_of_employee_value.upper,
                ]

            payload = {
                **base_payload,
                "user_type": UserType.ORGANISATION.value,
                "organisation": {
                    "org_id": str(user.uuid),
                    "organisation_name": user.organisation_name,
                    "ceo_first_name": user.ceo_first_name,
                    "ceo_last_name": user.ceo_last_name,
                    "email": user.email,
                    "no_of_employee": no_of_employee_value,
                    "website_link": user.website_link,
                    "linkedin": user.linkedin,
                },
            }
        else:
            date_of_birth = user.date_of_birth
            if isinstance(date_of_birth, date):
                date_of_birth = date_of_birth.isoformat()
            payload = {
                **base_payload,
                "user_type": user.user_type,
                "user": {
                    "user_id": str(user.uuid),
                    "title": user.title,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "organisation_name": user.organisation_name,
                    "email": user.email,
                    "gender": user.gender,
                    "date_of_birth": date_of_birth,
                    "cell_phone_number_1": user.cell_phone_number_1,
                },
            }

        access_token = self.create_access_jwt(payload)
        return access_token

    def create_tokens(
            self, request: Request, user: BaseModel, otp_validated: bool, social_login: bool = False
    ) -> AccessJWT:
        base_payload = {
            "otp_validated": otp_validated,
            "iat": datetime.utcnow(),
            "social_login": social_login
        }

        profile_picture = (
            user.profile_picture
            if user.profile_picture and url(user.profile_picture)
            else f"{request.base_url}{user.profile_picture}" if user.profile_picture
            else None
        )

        if isinstance(user, Organisation):
            no_of_employee_value = user.no_of_employee
            if isinstance(no_of_employee_value, Range):
                no_of_employee_value = [
                    no_of_employee_value.lower,
                    no_of_employee_value.upper,
                ]

            payload = {
                **base_payload,
                "user_type": UserType.ORGANISATION.value,
                "organisation": {
                    "user_type": UserType.ORGANISATION.value,
                    "org_id": str(user.uuid),
                    "organisation_name": user.organisation_name,
                    "ceo_first_name": user.ceo_first_name,
                    "ceo_last_name": user.ceo_last_name,
                    "email": user.email,
                    "no_of_employee": no_of_employee_value,
                    "website_link": user.website_link,
                    "linkedin": user.linkedin,
                    "profile_picture": profile_picture
                },
            }
        else:
            date_of_birth = user.date_of_birth
            if isinstance(date_of_birth, date):
                date_of_birth = date_of_birth.isoformat()
            payload = {
                **base_payload,
                "user_type": user.user_type,
                "user": {
                    "user_type": user.user_type,
                    "user_id": str(user.uuid),
                    "title": user.title,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "organisation_name": user.organisation_name,
                    "email": user.email,
                    "gender": user.gender,
                    "date_of_birth": date_of_birth,
                    "cell_phone_number_1": user.cell_phone_number_1,
                    "profile_picture": profile_picture
                },
            }

        access_token = self.create_access_jwt(payload)
        refresh_token = self.create_refresh_jwt(
            {"sub": str(user.uuid), "type": "refresh"}
        )

        return AccessJWT(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=settings.JWT_TYPE,
        )

    # def create_access_jwt(self, user: BaseModel, otp_validated: bool) -> AccessJWT:
    #     base_payload = {
    #         "otp_validated": otp_validated
    #     }
    #     if isinstance(user, Organisation):
    #         no_of_employee_value = user.no_of_employee
    #         if isinstance(no_of_employee_value, Range):
    #             no_of_employee_value = [no_of_employee_value.lower, no_of_employee_value.upper]
    #         payload = {
    #             **base_payload,
    #             "user_type": UserType.ORGANISATION.value,
    #             "organisation": {
    #                 "org_id": str(user.uuid),
    #                 "organisation_name": user.organisation_name,
    #                 "ceo_first_name": user.ceo_first_name,
    #                 "ceo_last_name": user.ceo_last_name,
    #                 "email": user.email,
    #                 "no_of_employee": no_of_employee_value,
    #                 "website_link": user.website_link,
    #                 "linkedin": user.linkedin,
    #             },
    #         }
    #     else:
    #         payload = {
    #             **base_payload,
    #             "user_type": user.user_type,
    #             "user": {
    #                 "user_id": str(user.uuid),
    #                 "title": user.title,
    #                 "first_name": user.first_name,
    #                 "last_name": user.last_name,
    #                 "organisation_name": user.organisation_name,
    #                 "email": user.email,
    #                 "gender": user.gender,
    #                 "date_of_birth": user.date_of_birth,
    #                 "cell_phone_number_1": user.cell_phone_number_1,
    #             },
    #         }
    #     token = self.create_jwt(payload)
    #     return AccessJWT(access_token=token, token_type=settings.JWT_TYPE)

    async def request_password_reset(self, email: str):
        user = await UserRepository.get_one(self.db, email=email)
        if not user:
            user = await OrganisationRepository.get_one(self.db, email=email)
            if not user:
                raise RecordNotExistsError

        payload = {"sub": user.email}
        reset_token = self.create_jwt(payload)

        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        subject = "Password Reset Request"
        body = f"<p>Click on the link to reset your password: {reset_link}</p>"
        await EmailService.send([user.email], subject, body)

    async def reset_password(self, token: str, new_password: SecretStr):
        try:
            payload = self.decode_jwt(token)
            email = payload.get("sub")
            if email is None:
                raise InvalidTokenError

        except JWTError:
            raise InvalidTokenError

        user = await UserRepository.get_one(self.db, email=email)
        if not user:
            user = await OrganisationRepository.get_one(self.db, email=email)
            if not user:
                raise RecordNotExistsError

        hashed_password = self.hash_password(new_password.get_secret_value())
        if isinstance(user, Organisation):
            await OrganisationRepository.update_all(
                self.db, data={"password": hashed_password}, uuid=user.uuid
            )
        else:
            await UserRepository.update_all(
                self.db, data={"password": hashed_password}, uuid=user.uuid
            )

    async def send_reset_password_otp_mail(self, email: EmailStr):
        user = await UserRepository.get_one(self.db, email=email)
        if not user:
            user = await OrganisationRepository.get_one(self.db, email=email)
            if not user:
                raise RecordNotExistsError

        otp = self.generate_otp()

        subject = "OTP for Password Reset"
        body = f"<p>Reset password OTP: {otp}</p>"
        await EmailService.send([user.email], subject, body)

    async def verify_otp_reset_password(self, payload: OTPResetPassword):
        verified_otp = self.verify_otp(payload.otp)
        if not verified_otp:
            raise InvalidOTPError

        user = await UserRepository.get_one(self.db, email=payload.email)
        if not user:
            user = await OrganisationRepository.get_one(self.db, email=payload.email)
            if not user:
                raise RecordNotExistsError

        hashed_password = self.hash_password(payload.new_password.get_secret_value())
        if isinstance(user, Organisation):
            await OrganisationRepository.update_all(
                self.db, data={"password": hashed_password}, uuid=user.uuid
            )
        else:
            await UserRepository.update_all(
                self.db, data={"password": hashed_password}, uuid=user.uuid
            )

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def create_jwt(payload_data: Dict[str, Any]) -> str:
        payload_data.update(
            {
                "iat": datetime.now().timestamp(),
                "exp": (
                    datetime.now() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
                ).timestamp(),
            }
        )
        encoded_jwt = jwt.encode(
            payload_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_access_jwt(payload_data: Dict[str, Any]) -> str:
        payload_data.update(
            {
                "iat": datetime.now().timestamp(),
                "exp": (
                    datetime.now() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
                ).timestamp(),
            }
        )
        encoded_jwt = jwt.encode(
            payload_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_jwt(payload_data: Dict[str, Any]) -> str:
        payload_data.update(
            {
                "iat": datetime.now().timestamp(),
                "exp": (
                    datetime.now()
                    + timedelta(days=int(settings.JWT_REFRESH_EXPIRE_DAYS))
                ).timestamp(),
            }
        )
        encoded_jwt = jwt.encode(
            payload_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_jwt(token: str) -> Dict[str, Any]:
        decoded_token = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded_token

    async def refresh_access_token(self, refresh_token: str) -> AccessJWT:
        """Refresh the access token using a valid refresh token."""
        try:
            payload = self.decode_jwt(refresh_token)
            if payload.get("type") != "refresh":
                raise InvalidTokenError("Invalid token type.")

            user_id = payload.get("sub")
            user = await UserRepository.get_one(self.db, uuid=user_id)

            if not user:
                raise RecordNotExistsError("User not found.")

            return self.create_tokens(user, otp_validated=False)

        except JWTError as e:
            raise InvalidTokenError(f"Token decoding failed: {e}")

    @staticmethod
    def generate_otp():
        # otp_secret_key = pyotp.random_base32()
        totp = pyotp.TOTP(
            OTP_SECRET_KEY, interval=OTP_EXPIRE_SECONDS
        )  # OTP valid for 10 minutes
        return totp.now()

    @staticmethod
    def verify_otp(otp: str) -> bool:
        # otp_secret_key = pyotp.random_base32()
        totp = pyotp.TOTP(OTP_SECRET_KEY, interval=OTP_EXPIRE_SECONDS)
        return totp.verify(otp)

    async def oauth_login(self, request: Request, payload: OAuthCallbackPayload):
        try:
            provider_lower = payload.provider.lower()
            if provider_lower not in [provider.value for provider in OAuthProvider]:
                raise InvalidProviderError(
                    f"Unsupported OAuth provider: {payload.provider}"
                )

            if provider_lower == OAuthProvider.TWITTER.value:
                if not payload.code_verifier:
                    raise InvalidTokenError(
                        "code_verifier is required for Twitter OAuth"
                    )
                tokens = await self.exchange_oauth_code_for_tokens(
                    code=payload.code,
                    provider=provider_lower,
                    redirect_uri=payload.redirect_uri,
                    code_verifier=payload.code_verifier,
                    platform=payload.platform,
                )
            else:
                tokens = await self.exchange_oauth_code_for_tokens(
                    code=payload.code,
                    provider=provider_lower,
                    redirect_uri=payload.redirect_uri,
                    code_verifier=None,
                    platform=payload.platform,
                )

            if provider_lower in [
                OAuthProvider.LINKEDIN.value,
                OAuthProvider.FACEBOOK.value,
                OAuthProvider.TWITTER.value,
            ]:
                id_token_str = tokens.get("access_token")
            else:
                id_token_str = tokens.get("id_token")

            if not id_token_str:
                raise InvalidTokenError(
                    "ID token not found in the response from the provider"
                )

            if provider_lower == OAuthProvider.YAHOO.value:
                decoded_data_from_id_token = await self.decode_oauth_id_token(
                    id_token_str,
                    provider_lower,
                    tokens.get("access_token"),
                    payload.platform,
                )
            else:
                decoded_data_from_id_token = await self.decode_oauth_id_token(
                    id_token_str, provider_lower, None, payload.platform
                )

            decoded_data_from_id_token.update(
                {"access_token": tokens.get("access_token")}
            )
            decoded_data_from_id_token.update(
                {"refresh_token": tokens.get("refresh_token")}
            )

            if provider_lower in [
                OAuthProvider.FACEBOOK.value,
                OAuthProvider.TWITTER.value,
            ]:
                oauth_id = decoded_data_from_id_token.get("id")
            else:
                oauth_id = decoded_data_from_id_token.get("sub")

            if not oauth_id:
                raise InvalidTokenError("OAuth ID not found in the decoded token")

            user_email = decoded_data_from_id_token.get("email", "")
            # if not user_email:
            #     raise InvalidTokenError("Email not found in the decoded token")

            if provider_lower == OAuthProvider.FACEBOOK.value:
                given_name = decoded_data_from_id_token.get("name", "")
                family_name = decoded_data_from_id_token.get("family_name", "")
                pictureObj = decoded_data_from_id_token.get("picture", None)
                picture = ""
                if pictureObj and isinstance(pictureObj, dict):
                    picture_data = pictureObj.get("data", None)
                    if picture_data and isinstance(picture_data, dict):
                        picture = picture_data.get("url", "")
            elif provider_lower == OAuthProvider.TWITTER.value:
                given_name = decoded_data_from_id_token.get("name", "")
                family_name = decoded_data_from_id_token.get("family_name", "")
                picture = decoded_data_from_id_token.get("picture", None)
            elif provider_lower == OAuthProvider.ZOHO.value:
                given_name = decoded_data_from_id_token.get("first_name", "")
                family_name = decoded_data_from_id_token.get("last_name", "")
                picture = decoded_data_from_id_token.get("profile_picture", None)
            else:
                given_name = decoded_data_from_id_token.get("given_name", "")
                family_name = decoded_data_from_id_token.get("family_name", "")
                picture = decoded_data_from_id_token.get("picture", None)

            user = await UserRepository.get_by_oauth_id_and_provider(
                oauth_id=oauth_id, oauth_provider=payload.provider
            )

            if user:
                # Create JWT for the newly created or updated user
                updated_user = await UserRepository.update(
                    user_id=user.uuid,
                    data={"oauth_details": json.dumps(decoded_data_from_id_token)},
                )

                return_data = self.create_tokens(
                    request=request,
                    user=updated_user if updated_user else user,
                    otp_validated=False,
                    social_login=True
                )
                return APIResponse.success(
                    message="User already exists, login successful.", data=return_data
                )

            user = User(
                email=None,
                oauth_email=user_email if user_email else None,
                oauth_provider=payload.provider,
                oauth_id=oauth_id,
                first_name=given_name,
                last_name=family_name,
                profile_picture=picture,
                password="",
                oauth_details=json.dumps(decoded_data_from_id_token),
                user_type=payload.user_type.value,
                gender=payload.gender.value,
                date_of_birth=None,
                country_code=None,
                cell_phone_number_1=None,
                cell_phone_number_2=None,
                landline=None,
                role_id=None,
                organisation_name=None,
                title=None,
            )
            await UserRepository.create(self.db, instance=user)

            return_data = self.create_tokens(
                request=request, user=user, otp_validated=False, social_login=True
            )
            return APIResponse.success(
                message="New user created, login successful.", data=return_data
            )

        except InvalidProviderError as e:
            return APIResponse.error(
                status_code=400,
                message=f"Unsupported OAuth provider: {str(e)}",
            )
        except InvalidTokenError as e:
            return APIResponse.error(
                status_code=400,
                message=f"Invalid token: {str(e)}",
            )
        except UserAlreadyExistsError as e:
            return APIResponse.error(
                status_code=409,
                message=f"User already exists: {str(e)}",
            )
        except Exception as ex:
            return APIResponse.error(
                status_code=500,
                message=f"An unexpected error occurred: {str(ex)}",
            )

    @staticmethod
    def user_to_dict(user: User):
        return {
            "id": str(user.uuid),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_picture": user.profile_picture,
            "oauth_provider": user.oauth_provider,
            "oauth_id": user.oauth_id,
            "oauth_details": user.oauth_details,
        }

    async def exchange_oauth_code_for_tokens(
        self,
        code: str,
        provider: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
        platform: Optional[str] = "web",
    ) -> Dict[str, Any]:
        if provider == OAuthProvider.GOOGLE.value:
            if platform == "web":
                CLIENT_ID = GOOGLE_WEB_CLIENT_ID
            elif platform == "ios":
                CLIENT_ID = GOOGLE_IOS_CLIENT_ID

            token_url = "https://oauth2.googleapis.com/token"
            client_id = CLIENT_ID
            client_secret = GOOGLE_CLIENT_SECRET
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

        elif provider == OAuthProvider.FACEBOOK.value:
            token_url = "https://graph.facebook.com/v10.0/oauth/access_token"
            client_id = FACEBOOK_CLIENT_ID
            client_secret = FACEBOOK_CLIENT_SECRET
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

        elif provider == OAuthProvider.INSTAGRAM.value:
            token_url = "https://api.instagram.com/oauth/access_token"
            client_id = INSTAGRAM_CLIENT_ID
            client_secret = INSTAGRAM_CLIENT_SECRET
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

        elif provider == OAuthProvider.LINKEDIN.value:
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            client_id = LINKEDIN_CLIENT_ID
            client_secret = LINKEDIN_CLIENT_SECRET
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

        elif provider == OAuthProvider.TWITTER.value:
            token_url = "https://api.twitter.com/2/oauth2/token"
            client_id = TWITTER_CLIENT_ID
            client_secret = TWITTER_CLIENT_SECRET

            if not code_verifier:
                raise InvalidTokenError("code_verifier is required for Twitter OAuth")

            credentials = f"{client_id}:{client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_credentials}",
            }

            data = {
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
            }

        elif provider == OAuthProvider.YAHOO.value:
            token_url = "https://api.login.yahoo.com/oauth2/get_token"
            client_id = YAHOO_CLIENT_ID
            client_secret = YAHOO_CLIENT_SECRET
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

        elif provider == OAuthProvider.APPLE.value:
            token_url = "https://appleid.apple.com/auth/token"
            client_id = APPLE_CLIENT_ID
            client_secret = APPLE_CLIENT_SECRET
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

        elif provider == OAuthProvider.ZOHO.value:
            token_url = "https://accounts.zoho.in/oauth/v2/token"
            client_id = ZOHO_CLIENT_ID
            client_secret = ZOHO_CLIENT_SECRET
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

        else:
            raise InvalidProviderError(f"Unsupported provider: {provider}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(token_url, data=data, headers=headers)
                response_json = response.json()
                if response.status_code == 200:
                    return response_json
                else:
                    error_description = response_json.get(
                        "error_description", response_json.get("error", "Unknown error")
                    )
                    raise AuthenticationFailedError(
                        f"Failed to fetch tokens from {provider} provider: {error_description}"
                    )
            except httpx.HTTPStatusError as http_err:
                raise AuthenticationFailedError(
                    f"HTTP error during token exchange: {http_err}"
                ) from http_err
            except httpx.RequestError as req_err:
                raise AuthenticationFailedError(
                    f"Request error during token exchange: {req_err}"
                ) from req_err
            except ValueError as json_err:
                raise AuthenticationFailedError(
                    f"JSON decoding failed during token exchange: {json_err}"
                ) from json_err
            except Exception as e:
                raise AuthenticationFailedError(
                    f"An unexpected error occurred during token exchange: {e}"
                ) from e

    @staticmethod
    async def decode_oauth_id_token(
        id_token_str: str, provider: str, access_token: Optional[str], platform: str
    ):
        if provider == OAuthProvider.GOOGLE.value:
            return await AuthService.decode_google_data(id_token_str, platform)

        elif provider == OAuthProvider.FACEBOOK.value:
            return await AuthService.decode_facebook_data(id_token_str)

        elif provider == OAuthProvider.INSTAGRAM.value:
            return await AuthService.decode_instagram_data(id_token_str)

        elif provider == OAuthProvider.LINKEDIN.value:
            return await AuthService.decode_linkedin_data(id_token_str)

        elif provider == OAuthProvider.TWITTER.value:
            return await AuthService.decode_twitter_data(id_token_str)

        elif provider == OAuthProvider.YAHOO.value:
            return await AuthService.decode_yahoo_data(access_token, id_token_str)

        elif provider == OAuthProvider.APPLE.value:
            return await AuthService.decode_apple_data(id_token_str)

        elif provider == OAuthProvider.ZOHO.value:
            return await AuthService.decode_zoho_data(id_token_str)

        else:
            raise InvalidTokenError("Not supported")

    @staticmethod
    async def decode_google_data(id_token_str: str, platform):
        try:
            if platform == "web":
                decoded_token = id_token.verify_oauth2_token(
                    id_token_str, requests.Request(), GOOGLE_WEB_CLIENT_ID
                )
            elif platform == "ios":
                decoded_token = id_token.verify_oauth2_token(
                    id_token_str, requests.Request(), GOOGLE_IOS_CLIENT_ID
                )

            return decoded_token
        except ValueError as e:
            raise InvalidTokenError(f"Error decoding Google ID token: {e}")

    @staticmethod
    async def decode_facebook_data(id_token_str: str):
        user_info_url = "https://graph.facebook.com/me?fields=id,name,email,picture"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                user_info_url, params={"access_token": id_token_str}
            )
            if response.status_code != 200:
                raise InvalidTokenError(
                    f"Error fetching Facebook user info: {response.json()}"
                )
            return response.json()

    @staticmethod
    async def decode_instagram_data(id_token_str: str):
        user_info_url = "https://graph.instagram.com/me?fields=id,username,account_type"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                user_info_url, params={"access_token": id_token_str}
            )
            if response.status_code != 200:
                raise InvalidTokenError(
                    f"Error fetching Instagram user info: {response.json()}"
                )
            return response.json()

    @staticmethod
    async def decode_linkedin_data(id_token_str: str):
        user_info_url = "https://api.linkedin.com/v2/userinfo"
        headers = {"Authorization": f"Bearer {id_token_str}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            if response.status_code != 200:
                raise InvalidTokenError(
                    f"Error fetching LinkedIn user info: {response.json()}"
                )
            return response.json()

    @staticmethod
    async def decode_yahoo_data(access_token: str, id_token_str: str):
        user_info_url = (
            f"https://api.login.yahoo.com/openid/v1/userinfo?id_token={id_token_str}"
        )
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            if response.status_code != 200:
                raise InvalidTokenError(
                    f"Error fetching Yahoo user info: {response.json()}"
                )
            return response.json()

    @staticmethod
    async def decode_apple_data(id_token_str: str):
        # Apple requires the ID token to be decoded as a JWT
        try:
            # Replace APPLE_PUBLIC_KEY with your actual Apple public key
            decoded_token = jwt.decode(
                id_token_str,
                APPLE_PUBLIC_KEY,
                algorithms=["RS256"],
                audience=APPLE_CLIENT_ID,
            )
            return decoded_token
        except JWTError as e:
            raise InvalidTokenError(f"Error decoding Apple ID token: {e}")

    @staticmethod
    async def decode_twitter_data(access_token: str):
        user_info_url = "https://api.twitter.com/2/users/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "YourAppNameHere",  # Replace with your actual User-Agent
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(user_info_url, headers=headers)
                response.raise_for_status()
                user_data = response.json()

                if "data" not in user_data or "id" not in user_data["data"]:
                    raise InvalidTokenError(
                        "Incomplete user information received from Twitter."
                    )

                return user_data["data"]

            except httpx.HTTPStatusError as http_err:
                error_detail = response.json().get("error", response.text)
                raise InvalidTokenError(
                    f"HTTP error occurred while fetching Twitter user info: {error_detail}"
                ) from http_err
            except httpx.RequestError as req_err:
                raise InvalidTokenError(
                    f"Request error occurred while fetching Twitter user info: {req_err}"
                ) from req_err
            except ValueError as json_err:
                raise InvalidTokenError(
                    f"JSON decoding failed for Twitter user info: {json_err}"
                ) from json_err
            except Exception as ex:
                raise InvalidTokenError(
                    f"An unexpected error occurred while fetching Twitter user info: {ex}"
                ) from ex

    @staticmethod
    async def decode_zoho_data(id_token_str: str):
        header, payload, signature = id_token_str.split(".")
        try:
            padding = "=" * (4 - len(payload) % 4)
            payload += padding
            decoded_payload = base64.urlsafe_b64decode(payload).decode("utf-8")
            payload_json = json.loads(decoded_payload)
            return payload_json
        except Exception as e:
            raise e
