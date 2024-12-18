from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.language import CreateLanguage
from app.services.language import LanguageService
from app.api.response import APIResponse

router = APIRouter(tags=["Language"])


@router.post("/language", status_code=status.HTTP_201_CREATED)
async def create_language(
    payload: CreateLanguage, service: LanguageService = Depends(LanguageService)
):
    response_data = await service.create(payload=payload, name=payload.name)
    return APIResponse.success(
        message="Language successfully created", data=response_data
    )


@router.get("/language", status_code=status.HTTP_200_OK)
async def get_all_language(service: LanguageService = Depends(LanguageService)):
    response_data = await service.get_all()
    return APIResponse.success(
        message="Successfully get list of all languages", data=response_data
    )


@router.put("/language/{language_id}", status_code=status.HTTP_200_OK)
async def update_language(
    language_id: str,
    payload: CreateLanguage,
    service: LanguageService = Depends(LanguageService),
):
    response_data = await service.update(payload=payload, uuid=language_id)
    return APIResponse.success(
        message="Language Successfully updated", data=response_data
    )


@router.delete("/language/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_language(
    language_id: str, service: LanguageService = Depends(LanguageService)
):
    await service.delete(uuid=language_id)
    return APIResponse.success(message="Language successfully deleted")
