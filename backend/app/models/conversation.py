from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from .base import Base

class MessageRole(enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class MessageType(enum.Enum):
    TEXT = "text"
    THINKING = "thinking"
    ERROR = "error"

class Conversation(Base):
    """会话模型"""
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True)  # 用户标识
    model: Mapped[str] = mapped_column(String(50))  # 使用的模型
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    
    @property
    def messages_list(self) -> list["Message"]:
        """返回已加载的消息列表"""
        return list(self.messages)

class Message(Base):
    """消息模型"""
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversation.id"))
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))
    type: Mapped[MessageType] = mapped_column(Enum(MessageType), default=MessageType.TEXT)
    content: Mapped[str] = mapped_column(Text)
    tokens: Mapped[Optional[int]] = mapped_column(nullable=True)  # token数量
    conversation: Mapped[Conversation] = relationship(back_populates="messages") 