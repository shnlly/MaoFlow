from sqlalchemy import String, Text, Enum, JSON, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .conversation  import Conversation
from core.base_model import Base
import enum
from typing import List

class MessageRole(enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class MessageType(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"


class Message(Base):
    """消息模型"""
    __tablename__ = "message"

    # 消息内容和类型
    content: Mapped[str] = mapped_column(Text)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))
    type: Mapped[MessageType] = mapped_column(
        Enum(MessageType),
        default=MessageType.TEXT
    )

    # 消息处理信息
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    processing_time: Mapped[float] = mapped_column(default=0.0)  # 处理时间（秒）

    # 元数据
    meta_info: Mapped[dict] = mapped_column(
        JSON,
        default=lambda: {}
    )

    # 关联信息
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)

    # 关系定义
    conversation: Mapped[Conversation] = relationship(
        "Conversation",
        foreign_keys=[conversation_id],
        primaryjoin="Message.conversation_id == Conversation.id",
        lazy="joined"
    )

    # 添加message_items关系
    message_items: Mapped[List["MessageItem"]] = relationship(
        "MessageItem",
        primaryjoin="Message.id == MessageItem.message_id",
        foreign_keys="MessageItem.message_id",
        backref="message",
        lazy="joined"
    )
