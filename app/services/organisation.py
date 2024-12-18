import uuid
from urllib.request import Request

from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositories.organisation import OrganisationRepository
from app.schemas.organisation import UpdateOrganisation, GetOrganisationResponse
from app.services.auth import AuthService
from app.common.errors import OrganisationNotFoundError, OrganisationAlreadyExistsError
from ..config.pg_database import get_db


class OrganisationService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def get_organisation_list(self, request: Request):
        orgs = await OrganisationRepository.get_all(self.db)
        if not orgs:
            raise OrganisationNotFoundError

        return [GetOrganisationResponse.from_orm(request, org) for org in orgs]

    async def update_organisation_by_id(
        self, request: Request, org_id: uuid.UUID, payload: UpdateOrganisation
    ):
        user = await OrganisationRepository.get_one(self.db, uuid=org_id)
        if not user:
            raise OrganisationNotFoundError

        if payload.email and payload.email != user.email:
            existing_user = await OrganisationRepository.exists(
                self.db, email=payload.email
            )
            if existing_user:
                raise OrganisationAlreadyExistsError(
                    message="Organisation already exists with this email"
                )

        update_data = payload.dict(exclude_unset=True)
        password = update_data.get("password")
        if password:
            update_data["password"] = AuthService.hash_password(password)
        await OrganisationRepository.update_all(self.db, data=update_data, uuid=org_id)

        updated_org = await OrganisationRepository.get_one(self.db, uuid=org_id)
        return GetOrganisationResponse.from_orm(request, updated_org)

    async def delete_organisation_by_id(self, org_id: uuid.UUID):
        org = await OrganisationRepository.get_one(self.db, uuid=org_id)
        if not org:
            raise OrganisationNotFoundError

        await OrganisationRepository.delete(self.db, instance=org)

    async def delete_organisation_by_email(self, email: str):
        org = await OrganisationRepository.get_one(self.db, email=email)
        if not org:
            raise OrganisationNotFoundError

        await OrganisationRepository.delete(self.db, instance=org)

    async def get_organisation_by_email(self, request: Request, email: str):
        org = await OrganisationRepository.get_one(self.db, email=email)
        if not org:
            raise OrganisationNotFoundError
        return GetOrganisationResponse.from_orm(request, org)

    async def get_organisation_by_id(self, request: Request, user_id: uuid.UUID):
        org = await OrganisationRepository.get_one(self.db, uuid=user_id)
        if not org:
            raise OrganisationNotFoundError
        return GetOrganisationResponse.from_orm(request, org)
