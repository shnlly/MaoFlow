from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, JSON, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.llm.models.model import LLMModel
from core.base_model import Base

class Conversation(Base):
    """会话模型"""
    __tablename__ = "conversation"

    # 基本信息
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 会话设置和状态
    model_id: Mapped[str] = mapped_column(String(36), index=True)
    model: Mapped[LLMModel] = relationship(
        "LLMModel",
        foreign_keys=[model_id],
        primaryjoin="Conversation.model_id == LLMModel.id",
        lazy="joined"
    )
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",  # active, archived, deleted
        index=True
    )
    
    # 统计信息
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # 元数据
    meta_info: Mapped[dict] = mapped_column(
        JSON,
        default=lambda: {"tags": [], "custom_settings": {}}
    )
    
    # 用户关联
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    
    def update_stats(self, messages_count: int = 0, tokens: int = 0) -> None:
        """更新会话统计信息"""
        self.message_count += messages_count
        self.total_tokens += tokens
        self.last_message_at = datetime.utcnow()

