from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class CreateLanguage(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=2)


class CreateUserLanguage(BaseModel):
    user_id: UUID
    language_id: UUID


# ============================ [Response Models] ======================================
class LanguageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    name: str
    code: str

    @classmethod
    def from_orm(cls, language_orm):
        return cls(
            uuid=str(language_orm.uuid), name=language_orm.name, code=language_orm.code
        )


class UserLanguageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    user_id: str
    language_id: str

    @classmethod
    def from_orm(cls, language_orm):
        return cls(
            uuid=str(language_orm.uuid),
            user_id=str(language_orm.user_id),
            language_id=str(language_orm.language_id),
        )
