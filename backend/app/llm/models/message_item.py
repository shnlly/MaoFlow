from core.base_model import Base
from sqlalchemy import String, Text, Enum, JSON, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class MessageItem(Base):
    """消息区块节点模型"""
    __tablename__ = "message_item"

    # 基本信息
    content: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50))  # thought, action, observation等

    # 关联信息
    message_id: Mapped[str] = mapped_column(String(36), index=True)
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)

    # 排序
    order: Mapped[int] = mapped_column(Integer, default=0)
