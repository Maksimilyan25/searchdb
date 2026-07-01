from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime


class DocumentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rubrics: List[str]
    text: str
    created_date: datetime


class DocumentCreate(BaseModel):
    id: int
    rubrics: List[str]
    text: str


class SearchResponse(BaseModel):
    documents: List[DocumentBase]
    total: int


class DeleteResponse(BaseModel):
    success: bool
    message: str
