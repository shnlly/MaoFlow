from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from ..models.conversation import MessageRole, MessageType

class MessageBase(BaseModel):
    """消息基础模型"""
    role: MessageRole
    type: MessageType = MessageType.TEXT
    content: str
    tokens: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class MessageCreate(MessageBase):
    """创建消息的请求模型"""
    pass

class MessageResponse(MessageBase):
    """消息的响应模型"""
    id: int
    conversation_id: int
    created_at: datetime
    updated_at: datetime

class ConversationBase(BaseModel):
    """会话基础模型"""
    title: str
    description: Optional[str] = None
    user_id: str
    model: str
    
    model_config = ConfigDict(from_attributes=True)

class ConversationCreate(ConversationBase):
    """创建会话的请求模型"""
    pass

class ConversationUpdate(BaseModel):
    """更新会话的请求模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ConversationResponse(ConversationBase):
    """会话的响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建响应模型"""
        return cls(
            id=obj.id,
            title=obj.title,
            description=obj.description,
            user_id=obj.user_id,
            model=obj.model,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            messages=obj.messages_list
        ) 