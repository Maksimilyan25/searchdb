from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import DbConnectionsHandler
from src.core.logging import logger
from src.api.routes import router
from src.services.search_service import SearchService
from src.utils.load_data import load_data


async def check_and_load_data():
    """Проверка и загрузка данных если БД пустая"""
    try:
        db_handler = DbConnectionsHandler(settings.DATABASE_URL)
        async with db_handler.session_factory() as session:
            from sqlalchemy import text

            result = await session.execute(text("SELECT COUNT(*) FROM documents"))
            count = result.scalar()

            if count == 0:
                logger.info("📂 БД пустая, загружаем данные...")
                await load_data()
            else:
                logger.info(f"✅ В БД уже есть {count} документов, пропускаем загрузку")

        await db_handler.engine_close()
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке данных: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan менеджер"""
    logger.info("🚀 Запуск приложения...")
    await check_and_load_data()
    db_handler = DbConnectionsHandler(settings.DATABASE_URL)
    if await db_handler.check_connection():
        logger.info("✅ Подключение к БД установлено")
    else:
        logger.error("❌ Ошибка подключения к БД")
    search_service = SearchService()
    await search_service.create_index()
    logger.info("✅ Подключение к Elasticsearch установлено")

    app.state.db_handler = db_handler
    app.state.search_service = search_service

    yield

    logger.info("🛑 Остановка приложения...")
    await search_service.close()
    await db_handler.engine_close()
    logger.info("✅ Соединения закрыты")


app = FastAPI(
    title="Document Search Service",
    description="Сервис поиска документов",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роуты
app.include_router(router, prefix="/api/v1", tags=["documents"])


@app.get("/")
async def root():
    return {"message": "Document Search Service", "version": "0.1.0", "docs": "/docs"}


@app.get("/health")
async def health(request: Request):
    """Проверка состояния сервиса"""
    status = {"status": "healthy", "database": False, "elasticsearch": False}

    if hasattr(request.app.state, "db_handler"):
        status["database"] = await request.app.state.db_handler.check_connection()

    if hasattr(request.app.state, "search_service"):
        try:
            await request.app.state.search_service.es.ping()
            status["elasticsearch"] = True
        except Exception:
            status["elasticsearch"] = False

    return status
