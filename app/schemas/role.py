from fastapi import Request
from pydantic import BaseModel, Field
from typing import Optional, List

from app.common.utils import format_timestamp


class CreateRole(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=254)


class UpdateRole(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=254)


class RoleResponse(BaseModel):
    uuid: str
    name: str
    description: Optional[str]
    created_at: str

    @classmethod
    def from_orm(cls, role_orm):
        return cls(
            uuid=str(role_orm.uuid),
            name=role_orm.name,
            description=role_orm.description,
            created_at=format_timestamp(role_orm.created_at),
        )

class DeleteRoleResponse(BaseModel):
    uuid: str

    @classmethod
    def from_orm(cls, role_orm):
        return cls(
            uuid=str(role_orm.uuid)
        )


class UsersRoleResponse(BaseModel):
    uuid: str
    name: str
    user_count: int
    profile_picture: Optional[List[str]]

    @classmethod
    def from_orm(cls, role_orm, request: Request, user_count: int, profile_picture: list[str] = []):
        profile_pictures = []
        if profile_picture != []:
            for profile_pic in profile_picture:
                if profile_pic and profile_pic != "" and "https" not in profile_pic:
                    profile_pictures.append(f"{request.base_url}{profile_pic}")
                elif "https" in profile_pic:
                    profile_pictures.append(profile_pic)
                else:
                    continue

        return cls(
            uuid=str(role_orm.uuid),
            name=role_orm.name,
            description=role_orm.description,
            user_count=user_count,
            profile_picture=profile_pictures[:2],
        )