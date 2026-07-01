from elasticsearch import AsyncElasticsearch
from typing import List
from fastapi import HTTPException, status
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Сервис для работы с Elasticsearch"""

    def __init__(self):
        self.es = AsyncElasticsearch(
            [settings.ELASTICSEARCH_URL],
            retry_on_timeout=True,
            max_retries=3,
            timeout=30,
        )
        self.index_name = settings.ELASTICSEARCH_INDEX

    async def create_index(self):
        """Создание индекса"""
        try:
            # Проверяем существование индекса
            exists = await self.es.indices.exists(index=self.index_name)

            if exists:
                logger.info(f"Индекс {self.index_name} уже существует")
                return

            # Маппинг
            mapping = {
                "mappings": {
                    "properties": {"id": {"type": "integer"}, "text": {"type": "text"}}
                }
            }

            await self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"✅ Создан индекс {self.index_name}")

        except Exception as e:
            error_str = str(e).lower()
            # Если индекс уже существует — считаем успехом
            if any(
                phrase in error_str
                for phrase in [
                    "resource_already_exists",
                    "already exists",
                    "index_already_exists",
                ]
            ):
                logger.info(f"Индекс {self.index_name} уже существует")
                return

            logger.error(f"Ошибка при создании индекса: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании индекса: {str(e)}",
            )

    async def index_document(self, doc_id: int, text: str):
        """Индексация документа"""
        try:
            await self.es.index(
                index=self.index_name,
                id=doc_id,
                body={"id": doc_id, "text": text},
                refresh=True,
            )
        except Exception as e:
            logger.error(f"Ошибка при индексации документа: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при индексации: {str(e)}",
            )

    async def search(self, query: str, size: int = 20) -> List[int]:
        """Поиск документов"""
        if not query or not query.strip():
            return []

        try:
            response = await self.es.search(
                index=self.index_name,
                body={
                    "query": {"match": {"text": {"query": query, "fuzziness": "AUTO"}}},
                    "size": size,
                },
            )
            hits = response.get("hits", {}).get("hits", [])
            return [int(hit["_source"]["id"]) for hit in hits]
        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при поиске: {str(e)}",
            )

    async def delete_document(self, doc_id: int) -> bool:
        """Удаление документа"""
        try:
            await self.es.delete(index=self.index_name, id=doc_id, refresh=True)
            return True
        except Exception as e:
            error_str = str(e).lower()
            if "not_found" in error_str or "index_not_found" in error_str:
                return True  # уже удалён — нормально
            logger.error(f"Ошибка при удалении документа: {e}")
            return False

    async def close(self):
        """Закрытие соединения"""
        await self.es.close()
