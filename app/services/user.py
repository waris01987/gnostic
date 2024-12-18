import os
import uuid
from typing import Optional
from fastapi import Depends, UploadFile, Request
from sqlalchemy.orm import Session, selectinload

from app.repositories.user import UserRepository
from app.repositories.organisation import OrganisationRepository
from app.schemas.user import (
    GetUserRolesResponse,
    UpdateIndividualUser,
    GetIndividualUserResponse,
)
from app.services.auth import AuthService
from app.models.user import User
from app.common.errors import UserNotFoundError, UserAlreadyExistsError
from .language import UserLanguageService
from ..common.context import UserContext
from ..config.pg_database import get_db
from ..config.settings import PROFILE_PICTURE_DIR
from ..models.language import UserLanguage
from ..schemas.language import CreateUserLanguage
from ..schemas.pagination import PaginatedResponse


# PROFILE_PICTURE_DIR = Path("app/profile_picture")
# PROFILE_PICTURE_DIR.mkdir(parents=True, exist_ok=True)


class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def update_user_by_id(
        self, request: Request, user_id: uuid.UUID, payload: UpdateIndividualUser
    ):
        user_language_service = UserLanguageService(self.db)
        user = await UserRepository.get_one(self.db, uuid=user_id)
        if not user:
            raise UserNotFoundError

        if payload.email and payload.email != user.email:
            existing_user = await UserRepository.exists(self.db, email=payload.email)
            if existing_user:
                raise UserAlreadyExistsError(
                    message="User already exists with this email"
                )

        if (
            payload.cell_phone_number_1
            and payload.cell_phone_number_1 != user.cell_phone_number_1
        ):
            existing_user = await UserRepository.exists(
                self.db, cell_phone_number_1=payload.cell_phone_number_1
            )
            if existing_user:
                raise UserAlreadyExistsError(
                    message="User already exists with this phone number"
                )

        update_data = payload.dict(exclude_unset=True)
        password = update_data.get("password")
        languages = update_data.get("languages")
        if password:
            update_data["password"] = AuthService.hash_password(password)
        if languages:
            for language in languages:
                if not await user_language_service.get_one(
                    user_id=user_id, language_id=language
                ):
                    user_language_obj = CreateUserLanguage(
                        user_id=user_id, language_id=language
                    )
                    await user_language_service.create(payload=user_language_obj)
            del update_data["languages"]
        await UserRepository.update_all(self.db, data=update_data, uuid=user_id)

        updated_user = await UserRepository.get_one(self.db, uuid=user_id)
        return GetIndividualUserResponse.from_orm(updated_user, request)

    async def update_profile_picture(
        self, request: Request, profile_picture: Optional[UploadFile] = None
    ):
        email = UserContext.get().get("email")
        user = await UserRepository.get_one(self.db, email=email)
        repository = UserRepository if user else OrganisationRepository
        user = user or await OrganisationRepository.get_one(self.db, email=email)
        if not user:
            raise UserNotFoundError

        if not os.path.exists(PROFILE_PICTURE_DIR):
            os.makedirs(PROFILE_PICTURE_DIR)

        file_location = None
        if profile_picture and profile_picture != "null":
            file_extension = profile_picture.filename.split(".")[-1]
            file_name = f"{user.uuid}.{file_extension}"
            file_location = os.path.join(PROFILE_PICTURE_DIR, file_name)

            with open(file_location, "wb") as file:
                content = await profile_picture.read()
                file.write(content)

        public_url = f"{request.base_url}{file_location}" if file_location else None
        update_data = {"profile_picture": file_location or ""}
        await repository.update_all(self.db, data=update_data, uuid=user.uuid)
        return {"file_path": public_url}

    async def get_user_list(self, request):
        users = await UserRepository.get_all(self.db)
        if not users:
            raise UserNotFoundError

        return [GetIndividualUserResponse.from_orm(user, request) for user in users]

    async def get_user_roles(self, request, search_str, page, page_size):
        # users = await UserRepository.get_all(self.db, include_role=True)
        # if not users:
        #     raise UserNotFoundError

        users, pagination_details = await UserRepository.get_paginated(
            self.db, include_role=True, search=search_str, search_columns=["first_name", "last_name", "email"],
            page=page, page_size=page_size)
        if not users:
            raise UserNotFoundError

        return PaginatedResponse(
            data=[GetUserRolesResponse.from_orm(user, request) for user in users],
            pagination=pagination_details
        )

    async def delete_user_by_id(self, user_id: uuid.UUID):
        user = await UserRepository.get_one(self.db, uuid=user_id)
        if not user:
            raise UserNotFoundError

        await UserRepository.delete(self.db, instance=user)

    async def delete_user_by_email(self, email: str):
        user = await UserRepository.get_one(self.db, email=email)
        if not user:
            raise UserNotFoundError

        await UserRepository.delete(self.db, instance=user)

    async def get_user_by_email(self, request: Request, email: str):
        user = await UserRepository.get_one(self.db, email=email)
        if not user:
            raise UserNotFoundError
        return GetIndividualUserResponse.from_orm(user, request)

    async def get_user_by_id(self, request: Request, user_id: uuid.UUID | str):
        user = await UserRepository.get_one(
            self.db,
            uuid=user_id,
            options=[selectinload(User.languages).selectinload(UserLanguage.language)],
        )
        if not user:
            raise UserNotFoundError

        language_names = [
            {"code": language.language.code, "name": language.language.name}
            for language in user.languages
        ]
        return GetIndividualUserResponse.from_orm(
            user, request, language_names=language_names
        )
