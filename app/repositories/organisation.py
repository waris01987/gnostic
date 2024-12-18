from .base import BaseRepository
from app.models.organisation import Organisation


class OrganisationRepository(BaseRepository):
    ModelClass = Organisation
