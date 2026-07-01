from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional, Sequence
from src.models.document import Document


class DocumentRepository:
    """Репозиторий для работы с документами в БД"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document: Document) -> Document:
        """Создание документа"""
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_by_id(self, doc_id: int) -> Optional[Document]:
        """Получение документа по ID"""
        result = await self.db.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def get_by_ids(self, ids: List[int]) -> List[Document]:
        """Получение документов по списку ID"""
        if not ids:
            return []

        result = await self.db.execute(select(Document).where(Document.id.in_(ids)))
        documents: Sequence[Document] = result.scalars().all()

        # Сортируем в порядке ids
        doc_dict = {doc.id: doc for doc in documents}
        return [doc_dict[id] for id in ids if id in doc_dict]  # type: ignore

    async def delete(self, doc_id: int) -> bool:
        """Удаление документа по ID"""
        result = await self.db.execute(delete(Document).where(Document.id == doc_id))
        await self.db.commit()
        return result.rowcount > 0  # type: ignore

    async def get_all(self, limit: int = 1000) -> List[Document]:
        """Получение всех документов"""
        result = await self.db.execute(select(Document).limit(limit))
        documents: Sequence[Document] = result.scalars().all()
        return list(documents)
