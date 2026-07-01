import asyncio
import pandas as pd  # type: ignore
from src.core.database import DbConnectionsHandler
from src.core.config import settings
from src.services.document_service import DocumentService
from src.services.search_service import SearchService
from src.schemas.document import DocumentCreate
from src.core.logging import logger


async def load_data():
    """Загрузка данных из CSV в БД и Elasticsearch"""

    logger.info("Начало загрузки данных из CSV")

    try:
        df = pd.read_csv("data/posts.csv")  # type: ignore
        logger.info(f"Загружено {len(df)} строк из CSV")

        db_handler = DbConnectionsHandler(settings.DATABASE_URL)
        if not await db_handler.check_connection():
            logger.error("Нет подключения к БД")
            return

        async with db_handler.session_factory() as session:
            doc_service = DocumentService(session)
            search_service = SearchService()

            await search_service.create_index()
            logger.info("Индекс Elasticsearch готов")

            count = 0
            errors = 0

            for index, row in df.iterrows():  # type: ignore
                try:
                    rubrics = (
                        eval(row["rubrics"]) if isinstance(row["rubrics"], str) else []
                    )
                    # Используем индекс как id, а не row["id"]
                    doc_id = index + 1

                    doc = DocumentCreate(id=doc_id, rubrics=rubrics, text=row["text"])

                    await doc_service.create_document(doc)
                    await search_service.index_document(doc.id, doc.text)

                    count += 1

                    if count % 10 == 0:
                        logger.info(f"Загружено {count} документов")

                except Exception as e:
                    errors += 1
                    logger.error(f"Ошибка при загрузке документа {index}: {e}")
                    # Откатываем транзакцию при ошибке
                    await session.rollback()

            logger.info(f"Загружено {count} документов, ошибок: {errors}")

        await search_service.close()
        await db_handler.engine_close()
        logger.info("Соединения закрыты")

    except FileNotFoundError:
        logger.error("Файл data/posts.csv не найден")
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")


if __name__ == "__main__":
    asyncio.run(load_data())
