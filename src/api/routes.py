from fastapi import APIRouter, Query, status
from src.api.dependencies import DocumentServiceDep, SearchServiceDep
from src.schemas.document import SearchResponse, DeleteResponse

router = APIRouter()


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Поиск документов по тексту",
    description="Выполняет полнотекстовый поиск по документам в Elasticsearch. "
    "Возвращает первые 20 документов, отсортированных по дате создания (новые сверху). "
    "Минимальная длина запроса - 1 символ.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Успешный поиск"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Некорректный запрос (пустая строка)"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Ошибка сервера"},
    },
)
async def search_documents(
    document_service: DocumentServiceDep,
    search_service: SearchServiceDep,
    q: str = Query(
        ...,
        min_length=1,
        max_length=1000,
        description="Поисковый запрос. Поддерживает русскую морфологию и нечеткий поиск.",
        examples="python программирование",
    ),
):
    """Поиск документов по тексту"""
    doc_ids = await search_service.search(q, size=20)

    if not doc_ids:
        return SearchResponse(documents=[], total=0)

    documents = await document_service.get_documents_by_ids(doc_ids)
    documents.sort(key=lambda x: x.created_date, reverse=True)

    return SearchResponse(documents=documents, total=len(documents))


@router.delete(
    "/documents/{doc_id}",
    response_model=DeleteResponse,
    summary="Удаление документа",
    description="Удаляет документ по ID из базы данных и Elasticsearch индекса. "
    "Если документ не найден в БД или индексе, возвращает ошибку 404.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Документ успешно удален"},
        status.HTTP_404_NOT_FOUND: {"description": "Документ не найден"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Внутренняя ошибка сервера"
        },
    },
)
async def delete_document(
    doc_id: int,
    document_service: DocumentServiceDep,
    search_service: SearchServiceDep,
):
    """Удаление документа по ID из БД и индекса"""
    # Удаляем из БД
    await document_service.delete_document(doc_id)

    # Удаляем из Elasticsearch
    await search_service.delete_document(doc_id)

    return DeleteResponse(success=True, message=f"Документ {doc_id} успешно удален")
