from fastapi import APIRouter, Request
from fastapi.params import Depends
from starlette import status

from app.schemas.role import CreateRole, UpdateRole
from app.services.role import RoleService
from app.api.response import APIResponse

router = APIRouter(tags=["Role"])


@router.post(
    "/role",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Roles successfully created."},
        409: {"description": "Role with provided name already exists."},
    },
)
async def create_role(payload: CreateRole, service: RoleService = Depends(RoleService)):
    response_data = await service.create_role(payload=payload)
    return APIResponse.success(message="Role successfully created", data=response_data)


@router.get(
    "/roles",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of all roles."},
        404: {"description": "No roles found."},
    },
)
async def get_all_roles(
        search_str: str = None,
        page: int = None,
        page_size: int = None,
        service: RoleService = Depends(RoleService)):
    response_data = await service.get_all_roles(search_str=search_str, page=page, page_size=page_size)
    return APIResponse.success(message="Successfully get list of all roles", data=response_data)


@router.get(
    "/get_roles_user_count",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of all roles with user count."},
        404: {"description": "No roles found."},
    },
)
async def get_roles_user_count(
    request: Request, service: RoleService = Depends(RoleService)
):
    response_data = await service.get_roles_user_count(request)
    return APIResponse.success(
        message="Successfully get list of all roles with user counts.",
        data=response_data,
    )


@router.put(
    "/role/{role_id}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Role successfully updated."},
        404: {"description": "Role with provided ID not found."},
    },
)
async def update_role(
    role_id: str, payload: UpdateRole, service: RoleService = Depends(RoleService)
):
    response_data = await service.update_role(role_id=role_id, payload=payload)
    return APIResponse.success(message="Role Successfully updated", data=response_data)


@router.delete(
    "/role/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Role successfully deleted."},
        404: {"description": "Role with provided ID not found."},
    },
)
async def delete_role(role_id: str, service: RoleService = Depends(RoleService)):
    response_data = await service.delete_role(role_id=role_id)
    return APIResponse.success(message="Role successfully deleted", data=response_data)
