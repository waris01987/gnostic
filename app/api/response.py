import json
from starlette import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Union, List, Any


class APIErrorResponse(BaseModel):
    success: bool = False
    message: str
    details: Optional[dict] = None


class APISuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Any = None


class APIResponse:

    @staticmethod
    def success(message: str, data: Any = None, status_code: int = status.HTTP_200_OK):
        if isinstance(data, BaseModel):
            data = data.dict()  # Convert a single BaseModel instance to a dictionary
        elif isinstance(data, list):
            # Convert a list of BaseModel instances to a list of dictionaries
            data = [item.dict() if isinstance(item, BaseModel) else item for item in data]

        response_data = APISuccessResponse(message=message, data=data)
        return JSONResponse(content=response_data.dict(), status_code=status_code)

    @staticmethod
    def error(message: str, status_code: int = 400, details: dict = None):
        response_data = APIErrorResponse(message=message, details=details)
        return JSONResponse(content=dict(response_data), status_code=status_code)
