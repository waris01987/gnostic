from .base import BaseRepository
from app.models.language import Language, UserLanguage


class LanguageRepository(BaseRepository):
    ModelClass = Language


class UserLanguageRepository(BaseRepository):
    ModelClass = UserLanguage
