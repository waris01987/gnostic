import uuid
from fastapi import APIRouter, Request
from fastapi.params import Depends
from starlette import status

from app.schemas.organisation import UpdateOrganisation
from app.services.organisation import OrganisationService
from app.api.response import APIResponse

router = APIRouter(tags=["Organisation"])


@router.get("/organisation/{org_id}", status_code=status.HTTP_200_OK)
async def get_organisation(
    request: Request,
    org_id: uuid.UUID,
    service: OrganisationService = Depends(OrganisationService),
):
    response_data = await service.get_organisation_by_id(
        request=request, user_id=org_id
    )
    return APIResponse.success(message="Get Organisation", data=response_data)


@router.put("/organisation/{org_id}", status_code=status.HTTP_200_OK)
async def update_organisation(
    request: Request,
    org_id: uuid.UUID,
    payload: UpdateOrganisation,
    service: OrganisationService = Depends(OrganisationService),
):
    response_data = await service.update_organisation_by_id(
        request=request, org_id=org_id, payload=payload
    )
    return APIResponse.success(
        message="Organisation successfully updated.", data=response_data
    )


@router.get("/organisations", status_code=status.HTTP_200_OK)
async def get_organisation_list(
    request: Request, service: OrganisationService = Depends(OrganisationService)
):
    response_data = await service.get_organisation_list(request=request)
    return APIResponse.success(
        message="Successfully get all organisations", data=response_data
    )


@router.delete("/organisation/{org_id}", status_code=status.HTTP_200_OK)
async def delete_organisation(
    org_id: uuid.UUID, service: OrganisationService = Depends(OrganisationService)
):
    response_data = await service.delete_organisation_by_id(org_id=org_id)
    return APIResponse.success(
        message="Organisation successfully deleted.", data=response_data
    )
