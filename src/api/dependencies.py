from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.services.document_service import DocumentService
from src.services.search_service import SearchService


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_document_service(session: SessionDep) -> DocumentService:
    return DocumentService(session)


async def get_search_service() -> SearchService:
    return SearchService()


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]
