import pytest
from fastapi import status
from contextlib import suppress

from app.schemas.auth import IndividualRegistration, OrganisationRegistration
from app.services.auth import AuthService
from app.services.user import UserService
from app.services.organisation import OrganisationService

from tests.app.api.conftest import (
    unique_user_data,
    unique_organization_data,
    AuthServiceApiTestDriver,
)
from app.common.errors import UserNotFoundError, OrganisationNotFoundError


class TestAuthApi:
    # ======================= [Individual Registration] ===========================
    @pytest.mark.asyncio
    async def test_should_register_user_successfully(self, client, database):
        user_service = UserService(db=database)
        user_data = unique_user_data()
        try:
            response = client.post("/api/v1/registration/individual", json=user_data)
            assert response.status_code == status.HTTP_200_OK
            user = response.json()
            assert user["success"] == True
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=user_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_invalid_email(self, client, database):
        user_service = UserService(db=database)
        user_data = unique_user_data()
        user_data["email"] = "invalid-email"
        try:
            response = client.post("/api/v1/registration/individual", json=user_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email="invalid-email")

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_empty_password(self, client, database):
        user_service = UserService(db=database)
        user_data = unique_user_data()
        user_data["password"] = ""
        try:
            response = client.post("/api/v1/registration/individual", json=user_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=user_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_empty_email(self, client, database):
        user_service = UserService(db=database)
        user_data = unique_user_data()
        user_data["email"] = ""
        try:
            response = client.post("/api/v1/registration/individual", json=user_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email="")

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_duplicate_email(
        self, client, database
    ):
        user_service = UserService(db=database)
        user_data = unique_user_data()
        try:
            response = client.post("/api/v1/registration/individual", json=user_data)
            assert response.status_code == status.HTTP_200_OK

            response = client.post("/api/v1/registration/individual", json=user_data)
            assert response.status_code == status.HTTP_409_CONFLICT
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=user_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_user_with_duplicate_email(
        self, client, database
    ):
        async with (AuthServiceApiTestDriver(database) as auth_driver,):
            user_data = unique_user_data()
            await auth_driver.create_user(user_data)

            response = client.post("/api/v1/registration/individual", json=user_data)
            assert response.status_code == status.HTTP_409_CONFLICT

    # ======================= [Organisation Registration] ===========================
    @pytest.mark.asyncio
    async def test_should_register_organisation_successfully(self, client, database):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_200_OK
            user = response.json()
            assert user["success"] == True
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_organisation_with_invalid_email(
        self, client, database
    ):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()
        org_data["email"] = "invalid-email"
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email="invalid-email")

    @pytest.mark.asyncio
    async def test_should_not_register_organisation_with_empty_password(
        self, client, database
    ):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()
        org_data["password"] = ""
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_organisation_with_empty_email(
        self, client, database
    ):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()
        org_data["email"] = ""
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email="")

    @pytest.mark.asyncio
    async def test_should_not_register_organisation_with_duplicate_email(
        self, client, database
    ):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_200_OK

            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_409_CONFLICT
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_organisation_with_invalid_employee_range(
        self, client, database
    ):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()

        # Test case: Invalid employee range format (e.g., missing brackets)
        org_data["no_of_employee"] = "500,1000"
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_register_organisation_with_valid_closed_employee_range(
        self, client, database
    ):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()

        # Test case: Valid closed range [100,500]
        org_data["no_of_employee"] = "[100,500]"
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_200_OK
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_register_organisation_with_valid_open_ended_employee_range(
        self, client, database
    ):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()

        # Test case: Valid open-ended range [500,]
        org_data["no_of_employee"] = "[500,]"
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_200_OK
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_register_organisation_with_invalid_open_ended_employee_range(
        self, client, database
    ):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()

        # Test case: Invalid open-ended range with non-numeric lower bound
        org_data["no_of_employee"] = "[abc,]"
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_register_organisation_with_infinite_employee_range(
        self, client, database
    ):
        org_service = OrganisationService(db=database)
        org_data = unique_organization_data()

        org_data["no_of_employee"] = "[500,]"
        try:
            response = client.post("/api/v1/registration/organisation", json=org_data)
            assert response.status_code == status.HTTP_200_OK
        finally:
            with suppress(OrganisationNotFoundError):
                await org_service.delete_organisation_by_email(email=org_data["email"])

    # ======================= [Login] ===========================
    @pytest.mark.asyncio
    async def test_login_user_success(self, client, database):
        user_service = UserService(db=database)
        auth_service = AuthService(db=database)
        user_data = unique_user_data()
        try:
            await auth_service.individual_registration(
                payload=IndividualRegistration(**user_data)
            )
            response = client.post(
                "/api/v1/login",
                json={"email": user_data["email"], "password": user_data["password"]},
            )
            assert response.status_code == status.HTTP_200_OK
            access_token = response.json()["data"]["access_token"]
            assert access_token
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=user_data["email"])

    @pytest.mark.asyncio
    async def test_login_organisation_success(self, client, database):
        user_service = UserService(db=database)
        auth_service = AuthService(db=database)
        org_data = unique_organization_data()
        try:
            await auth_service.register_organisation(
                payload=OrganisationRegistration(**org_data)
            )
            response = client.post(
                "/api/v1/login",
                json={"email": org_data["email"], "password": org_data["password"]},
            )
            assert response.status_code == status.HTTP_200_OK
            access_token = response.json()["data"]["access_token"]
            assert access_token
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=org_data["email"])

    @pytest.mark.asyncio
    async def test_should_not_login_user_with_invalid_email(self, client):
        response = client.post(
            "/api/v1/login",
            json={"email": "invalid-email@invalid.com", "password": "password"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_should_not_login_user_with_invalid_password(self, client, database):
        user_service = UserService(db=database)
        auth_service = AuthService(db=database)
        user_data = unique_user_data()
        try:
            await auth_service.individual_registration(
                payload=IndividualRegistration(**user_data)
            )
            response = client.post(
                "/api/v1/login",
                json={"email": user_data["email"], "password": "invalid-password"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=user_data["email"])

    # ======================= [Reset Password] ===========================
    @pytest.mark.asyncio
    async def test_should_not_login_user_with_invalid_password(self, client, database):
        user_service = UserService(db=database)
        auth_service = AuthService(db=database)
        user_data = unique_user_data()
        try:
            await auth_service.individual_registration(
                payload=IndividualRegistration(**user_data)
            )
            response = client.post(
                "/api/v1/login",
                json={"email": user_data["email"], "password": "invalid-password"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        finally:
            with suppress(UserNotFoundError):
                await user_service.delete_user_by_email(email=user_data["email"])
