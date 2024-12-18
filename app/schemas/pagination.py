from pydantic import BaseModel
from typing import List, TypeVar, Generic

T = TypeVar("T", bound=BaseModel)


class PaginationDetails(BaseModel):
    current_page: int
    page_size: int
    total_records: int
    total_pages: int


class PaginatedResponse(Generic[T], BaseModel):
    data: List[T]
    pagination: PaginationDetails