from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import HTTPException, status

from src.repositories.document_repository import DocumentRepository
from src.schemas.document import DocumentBase, DocumentCreate
from src.models.document import Document


class DocumentService:
    """Сервис для работы с документами"""

    def __init__(self, db: AsyncSession):
        self.repository = DocumentRepository(db)

    async def create_document(self, doc_data: DocumentCreate) -> DocumentBase:
        """Создание документа"""
        try:
            document = Document(
                id=doc_data.id,
                rubrics=doc_data.rubrics,
                text=doc_data.text,
            )
            created = await self.repository.create(document)
            return DocumentBase.model_validate(created)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании документа: {str(e)}",
            )

    async def get_document_by_id(self, doc_id: int) -> Optional[DocumentBase]:
        """Получение документа по ID"""
        document = await self.repository.get_by_id(doc_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Документ с id {doc_id} не найден",
            )
        return DocumentBase.model_validate(document)

    async def get_documents_by_ids(self, ids: List[int]) -> List[DocumentBase]:
        """Получение документов по списку ID"""
        if not ids:
            return []

        documents = await self.repository.get_by_ids(ids)
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Документы не найдены"
            )
        return [DocumentBase.model_validate(doc) for doc in documents]

    async def delete_document(self, doc_id: int) -> bool:
        """Удаление документа по ID"""
        deleted = await self.repository.delete(doc_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Документ с id {doc_id} не найден",
            )
        return deleted

    async def get_all_documents(self, limit: int = 1000) -> List[DocumentBase]:
        """Получение всех документов"""
        documents = await self.repository.get_all(limit)
        return [DocumentBase.model_validate(doc) for doc in documents]
