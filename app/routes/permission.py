from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status
from typing import List

from app.schemas.permission import CreatePermission, UpdatePermission, BulkAssignRoles
from app.services.permission import PermissionService
from app.api.response import APIResponse

router = APIRouter(tags=["Permission"])


@router.post("/permission", status_code=status.HTTP_201_CREATED)
async def create_permission(
    payload: CreatePermission, service: PermissionService = Depends(PermissionService)
):
    response_data = await service.create_permission(payload=payload)
    return APIResponse.success(
        message="Permission successfully created", data=response_data
    )


@router.get("/permissions", status_code=status.HTTP_200_OK)
async def get_all_permissions(
        search_str: str = None,
        page: int = None,
        page_size: int = None,
        service: PermissionService = Depends(PermissionService)
):
    response_data = await service.get_all_permissions(search_str=search_str, page=page, page_size=page_size)
    return APIResponse.success(message="Successfully get list of all permissions", data=response_data)


@router.put("/permission/{permission_id}", status_code=status.HTTP_200_OK)
async def update_permission(
    permission_id: str,
    payload: UpdatePermission,
    service: PermissionService = Depends(PermissionService),
):
    response_data = await service.update_permission(
        payload=payload, permission_id=permission_id
    )
    return APIResponse.success(
        message="Permission Successfully updated", data=response_data
    )


@router.delete("/permission/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: str, service: PermissionService = Depends(PermissionService)
):
    response_data = await service.delete_permission(permission_id=permission_id)
    return APIResponse.success(message="Permission successfully deleted", data=response_data)


@router.get("/permission-roles", status_code=status.HTTP_200_OK)
async def get_permission_with_roles(
    service: PermissionService = Depends(PermissionService),
):
    response_data = await service.get_permission_roles()
    return APIResponse.success(
        message="Successfully get list of all permissions", data=response_data
    )


@router.put("/bulk-assign-roles", status_code=status.HTTP_200_OK)
async def update_permission(
    payload: List[BulkAssignRoles],
    service: PermissionService = Depends(PermissionService),
):
    response_data = await service.bulk_assign_roles(payload=payload)
    return APIResponse.success(data=response_data, message="Permissions roles updated successfully.")
