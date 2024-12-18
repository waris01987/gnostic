import uuid
from typing import Optional, Union

from fastapi import APIRouter, UploadFile, File, Request, Depends
from starlette import status

from app.middlewares.jwt_auth import JWTBearerSecurity
from app.schemas.user import (
    UpdateIndividualUser,
)
from app.services.user import UserService
from app.api.response import APIResponse

router = APIRouter(tags=["User"])


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    request: Request, user_id: uuid.UUID, service: UserService = Depends(UserService)
):
    response_data = await service.get_user_by_id(request, user_id=user_id)
    return APIResponse.success(message="Get Individual User", data=response_data)


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(JWTBearerSecurity(permission="get_all_users"))]
)
async def get_user_list(request: Request, service: UserService = Depends(UserService)):
    response_data = await service.get_user_list(request)
    return APIResponse.success(
        message="Users list successfully fetched.", data=response_data
    )


@router.get(
    "/user_roles",
    status_code=status.HTTP_200_OK,
)
async def get_user_roles(
        request: Request,
        search_str: str = None,
        page: int = None,
        page_size: int = None,
        service: UserService = Depends(UserService)):
    response_data = await service.get_user_roles(request, search_str=search_str, page=page, page_size=page_size)
    return APIResponse.success(
        message="User with roles successfully fetched.", data=response_data
    )


@router.put("/user/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    request: Request,
    user_id: uuid.UUID,
    payload: UpdateIndividualUser,
    service: UserService = Depends(UserService),
):
    response_data = await service.update_user_by_id(
        request, user_id=user_id, payload=payload
    )
    return APIResponse.success(
        message="Individual User successfully updated.", data=response_data
    )


@router.post("/user/upload-profile-picture", status_code=status.HTTP_200_OK)
async def upload_profile_picture(
    request: Request,
    profile_picture: Optional[Union[UploadFile, str]] = File(None),
    service: UserService = Depends(UserService),
):
    response_data = await service.update_profile_picture(
        request, profile_picture=profile_picture
    )
    return APIResponse.success(
        message="Profile picture uploaded successfully.", data=response_data
    )


@router.delete("/user/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: uuid.UUID, service: UserService = Depends(UserService)):
    response_data = await service.delete_user_by_id(user_id=user_id)
    return APIResponse.success(
        message="Individual User successfully deleted.", data=response_data
    )
