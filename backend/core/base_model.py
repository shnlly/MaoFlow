from datetime import datetime
import uuid
from typing import Optional
from sqlalchemy import DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """基础模型类"""
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def soft_delete(self) -> None:
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow() 