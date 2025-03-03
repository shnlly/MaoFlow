from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

from ..models.message import MessageRole, MessageType

class ConversationBase(BaseModel):
    """会话基础模型"""
    title: str
    description: Optional[str] = None
    user_id: str
    model: str
    
    model_config = ConfigDict(from_attributes=True)

class ConversationCreate(ConversationBase):
    """创建会话的请求模型"""
    system_prompt: Optional[str] = None
    meta_info: Dict[str, Any] = {"tags": [], "custom_settings": {}}

class ConversationUpdate(BaseModel):
    """更新会话的请求模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    status: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)

class ConversationResponse(ConversationBase):
    """会话的响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    system_prompt: Optional[str]
    status: str
    message_count: int
    total_tokens: int
    last_message_at: Optional[datetime]
    meta_info: Dict[str, Any]

class MessageBase(BaseModel):
    """消息基础模型"""
    content: str
    role: MessageRole
    type: MessageType = MessageType.TEXT
    
    model_config = ConfigDict(from_attributes=True)

class MessageCreate(MessageBase):
    """创建消息的请求模型"""
    conversation_id: str
    user_id: str
    meta_info: Dict[str, Any] = {}

class MessageResponse(MessageBase):
    """消息的响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    tokens: int
    processing_time: float
    conversation_id: str
    user_id: str
    meta_info: Dict[str, Any]

class MessageItemBase(BaseModel):
    """消息区块节点基础模型"""
    content: str
    type: str
    order: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class MessageItemCreate(MessageItemBase):
    """创建消息区块节点的请求模型"""
    message_id: str
    conversation_id: str

class MessageItemResponse(MessageItemBase):
    """消息区块节点的响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    message_id: str
    conversation_id: str 