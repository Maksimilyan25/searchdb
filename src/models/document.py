from typing import List
from sqlalchemy import BigInteger, String, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from datetime import datetime
from src.core.database import Base


class Document(Base):
    """Модель документа"""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    rubrics: Mapped[List[str]] = mapped_column(
        PG_ARRAY(String), nullable=False, default=[]
    )
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    __table_args__ = (Index("idx_documents_created_date", created_date.desc()),)
