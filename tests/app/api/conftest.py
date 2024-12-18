import os
import uuid
import pytest
import hashlib
from dotenv import load_dotenv
from fastapi.testclient import TestClient


from app.main import app
from app.config.pg_test_database import get_test_db
from app.config.pg_database import get_db
from app.schemas.auth import IndividualRegistration
from app.services.auth import AuthService
from app.services.organisation import OrganisationService
from app.services.user import UserService

load_dotenv()
app.dependency_overrides[get_db] = get_test_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def database():
    return next(get_test_db())


def current_test() -> str:
    return os.environ["PYTEST_CURRENT_TEST"]


def current_test_hash() -> str:
    unique_suffix = str(uuid.uuid4())
    test_identifier = current_test() + unique_suffix
    return hashlib.sha1(test_identifier.encode("utf8")).hexdigest()


def unique_user_data():
    test_hash = current_test_hash()
    first_name = f"First_{test_hash[:10]}"
    last_name = f"Last_{test_hash[:10]}"
    organisation_name = f"Org_{test_hash[:10]}"
    email = f"{first_name}.{last_name}@example.com"
    password = f"password_{test_hash[10:20]}"
    country_code = "+1"
    cell_phone_number_1 = (
        f"1234567890{test_hash[0:5]}"  # Example cell phone number format
    )
    gender = 1  # Assuming 1 represents male, adjust as needed
    country_code_str = "CA"
    return {
        "first_name": first_name,
        "last_name": last_name,
        "organisation_name": organisation_name,
        "email": email,
        "gender": gender,
        "country_code": country_code,
        "cell_phone_number_1": cell_phone_number_1,
        "password": password,
        "country_code_str": country_code_str,
    }


def unique_organization_data():
    test_hash = current_test_hash()
    organization_name = f"Org_{test_hash[:10]}"
    ceo_first_name = f"CEOFirst_{test_hash[:10]}"
    ceo_last_name = f"CEOLast_{test_hash[:10]}"
    email = f"{organization_name}@example.com"
    established_year = 2021  # Example year
    country = "CountryName"  # Example country
    no_of_employee = "[1,10]"  # Example range in the expected format
    website_link = f"https://{organization_name}.com"
    linkedin = f"https://linkedin.com/in/{organization_name}"
    return {
        "organisation_name": organization_name,
        "ceo_first_name": ceo_first_name,
        "ceo_last_name": ceo_last_name,
        "email": email,
        "established_year": established_year,
        "country": country,
        "no_of_employee": no_of_employee,
        "website_link": website_link,
        "linkedin": linkedin,
        "password": f"password_{test_hash[10:20]}",
    }


class AuthServiceApiTestDriver:
    def __init__(self, database):
        self.database = database
        self.auth_service = AuthService(db=database)
        self.user_service = UserService(db=database)
        self.org_service = OrganisationService(db=database)
        self.created_users = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.delete_user()

    async def create_user(self, user_data):
        user_obj = IndividualRegistration(**user_data)
        user = await self.auth_service.individual_registration(user_obj)
        self.created_users.append(user)
        return user

    async def delete_user(self):
        for user in self.created_users:
            await self.user_service.delete_user_by_id(user_id=user.uuid)
            self.created_users = []
