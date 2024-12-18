from fastapi import Depends
from sqlalchemy.orm import Session

from .base import BaseService
from app.schemas.language import LanguageResponse, UserLanguageResponse
from app.repositories.language import LanguageRepository, UserLanguageRepository
from ..config.pg_database import get_db


class LanguageService(BaseService):
    def __init__(self, db: Session = Depends(get_db)):
        repository = LanguageRepository
        super().__init__(db=db, repository=repository, response=LanguageResponse)


class UserLanguageService(BaseService):
    def __init__(self, db: Session = Depends(get_db)):
        repository = UserLanguageRepository
        super().__init__(db=db, repository=repository, response=UserLanguageResponse)
