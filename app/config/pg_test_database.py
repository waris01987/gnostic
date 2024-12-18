from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import SQLALCHEMY_TEST_DATABASE_URL


test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def get_test_db() -> TestSessionLocal:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
