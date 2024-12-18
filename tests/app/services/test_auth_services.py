import os

import pytest
from contextlib import suppress
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError

from app.services.organisation import OrganisationService
from conftest import unique_organization_data, unique_user_data, AuthServiceTestDriver
from app.common.errors import (
    UserNotFoundError,
    UserAlreadyExistsError,
    OrganisationAlreadyExistsError,
    OrganisationNotFoundError,
)
from app.schemas.auth import (
    IndividualRegistrationResponse,
    IndividualRegistration,
    OrganisationRegistration,
    OrganisationRegistrationResponse,
)
from app.services.auth import AuthService
from app.services.user import UserService
from tests.app.services.conftest import OrganisationServiceTestDriver

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]


class TestAuth:
    @pytest.mark.asyncio
    async def test_should_register_then_delete_a_user(self, database):
        """
        Test register user
        """
        auth_service = AuthService(db=database)
        user_service = UserService(db=database)
        user_data = unique_user_data()
        try:
            user_obj = IndividualRegistration(**user_data)
            user = await auth_service.individual_registration(user_obj)

            assert isinstance(user, IndividualRegistrationResponse)

            created_user = await user_service.get_user_by_id(
                request=None, user_id=user.uuid
            )
            assert created_user.first_name == user.first_name
            assert created_user.last_name == user.last_name
            assert created_user.email == user.email
            assert created_user.organisation_name == user.organisation_name
            assert created_user.cell_phone_number_1 == user.cell_phone_number_1
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=user_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_invalid_email(self, database):
        """Test register user with invalid email"""
        auth_service = AuthService(db=database)
        user_service = UserService(db=database)
        try:
            user_data = unique_user_data()
            user_obj = IndividualRegistration(**user_data)
            user_obj.email = "invalid-email"
            with pytest.raises(ValueError):
                await auth_service.individual_registration(user_obj)
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email="invalid-email")

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_empty_password(self, database):
        """
        Test register user with invalid password
        """
        user_data = unique_user_data()
        user_data["password"] = ""

        auth_service = AuthService(db=database)
        user_service = UserService(db=database)
        try:
            with pytest.raises(ValidationError):
                user_obj = IndividualRegistration(**user_data)
                await auth_service.individual_registration(user_obj)
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=user_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_empty_email(self, database):
        """
        Test register user with empty email
        """
        user_data = unique_user_data()
        auth_service = AuthService(db=database)
        user_service = UserService(db=database)
        try:
            user_obj = IndividualRegistration(**user_data)
            user_obj.email = ""
            with pytest.raises(ValueError):
                await auth_service.individual_registration(user_obj)
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email="")

    @pytest.mark.asyncio
    async def test_should_not_register_duplicate_user(self, database):
        """
        Test Duplicate user
        """
        async with AuthServiceTestDriver(database) as auth_driver:
            user_obj = IndividualRegistration(**unique_user_data())
            await auth_driver.create_user(user_obj)
            with pytest.raises(UserAlreadyExistsError):
                await auth_driver.auth_service.individual_registration(user_obj)

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_unsupported_values(self, database):
        """
        Test unsupported values
        """
        user_obj = IndividualRegistration(**unique_user_data())
        user_obj.email = "testusergmail.com"
        auth_service = AuthService(db=database)
        user_service = UserService(db=database)
        try:
            with pytest.raises(Exception):
                await auth_service.individual_registration(user_obj)
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=user_obj.email)

    # ======================== [Organisation] =======================================
    @pytest.mark.asyncio
    async def test_should_register_organisation_then_delete_a_user(self, database):
        """
        Test register Organisation
        """
        auth_service = AuthService(db=database)
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()
        try:
            org_obj = OrganisationRegistration(**org_data)
            org = await auth_service.register_organisation(org_obj)

            assert isinstance(org, OrganisationRegistrationResponse)

            created_org = await org_service.get_organisation_by_id(
                request=None, user_id=org.uuid
            )
            assert created_org.organisation_name == org.organisation_name
            assert created_org.ceo_first_name == org.ceo_first_name
            assert created_org.ceo_last_name == org.ceo_last_name
            assert created_org.email == org.email
            assert created_org.established_year == org.established_year
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_organisation_with_invalid_email(self, database):
        """Test register Organisation with invalid email"""
        auth_service = AuthService(db=database)
        org_service = OrganisationService(db=database)
        try:
            org_data = unique_organization_data()
            org_obj = OrganisationRegistration(**org_data)
            org_obj.email = "invalid-email"
            with pytest.raises(ValueError):
                await auth_service.register_organisation(org_obj)
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email="invalid-email")

    @pytest.mark.asyncio
    async def test_should_not_register_organisation_with_empty_password(self, database):
        """
        Test register Organisation with invalid password
        """
        org_data = unique_organization_data()
        org_data["password"] = ""

        auth_service = AuthService(db=database)
        org_service = OrganisationService(db=database)
        try:
            with pytest.raises(ValidationError):
                org_obj = OrganisationRegistration(**org_data)
                await auth_service.register_organisation(org_obj)
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_organisation_with_empty_email(self, database):
        """
        Test register Organisation with empty email
        """
        org_data = unique_organization_data()
        auth_service = AuthService(db=database)
        org_service = OrganisationService(db=database)
        try:
            org_obj = OrganisationRegistration(**org_data)
            org_obj.email = ""
            with pytest.raises(ValueError):
                await auth_service.register_organisation(org_obj)
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email="")

    @pytest.mark.asyncio
    async def test_should_not_register_duplicate_organisation(self, database):
        """
        Test Duplicate Organisation
        """
        async with OrganisationServiceTestDriver(database) as org_driver:
            org_obj = OrganisationRegistration(**unique_organization_data())
            await org_driver.create_org(org_obj)
            with pytest.raises(OrganisationAlreadyExistsError):
                await org_driver.auth_service.register_organisation(org_obj)

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_unsupported_values(self, database):
        """
        Test unsupported values
        """
        org_obj = OrganisationRegistration(**unique_organization_data())
        org_obj.email = "testusergmail.com"
        auth_service = AuthService(db=database)
        org_service = OrganisationService(db=database)
        try:
            with pytest.raises(Exception):
                await auth_service.register_organisation(org_obj)
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_obj.email)
