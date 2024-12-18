# import pytest
# from fastapi import status
# from contextlib import suppress
#
# from app.schemas.auth import IndividualRegistration, OrganisationRegistration
# from app.services.auth import AuthService
# from app.services.user import UserService
# from app.services.organisation import OrganisationService
#
# from tests.app.api.conftest import unique_user_data, unique_organization_data, AuthServiceApiTestDriver
# from app.common.errors import UserNotFoundError, OrganisationNotFoundError
#
#
# class TestUserApi:
#     # ======================= [Individual User] ===========================
#     @pytest.mark.asyncio
#     async def test_should_register_user_successfully(self, client, database):
#         user_service = UserService(db=database)
#         try:
#             response = client.post("/api/v1/user/{user_id}")
#             assert response.status_code == status.HTTP_200_OK
#             assert response.json() == {
#                   "success": True,
#                   "message": "Get Individual User",
#                   "data": {
#                         "uuid": "a0e63d0c-be88-4f60-bd04-59e19c722e1a",
#                         "first_name": "mksuthar",
#                         "last_name": "mksuthar",
#                         "organisation_name": "string",
#                         "email": "user003@example.com",
#                         "cell_phone_number_1": "string"
#                   }
#             }
#         finally:
#             with suppress(UserNotFoundError):
#                 await user_service.delete_user_by_email(email=user_data["email"])
