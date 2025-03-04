from typing import Optional, List
from pydantic import BaseModel

from app.llm.schemas.message_item import MessageItemResponse
from app.llm.models.message import MessageRole, MessageType

class MessageBase(BaseModel):
    content: str = ""
    role: MessageRole = MessageRole.USER
    type: MessageType = MessageType.TEXT
    meta_info: Optional[dict] = {}

class MessageCreate(MessageBase):
    conversation_id: str
    user_id: str

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    user_id: str
    tokens: int = 0
    processing_time: float = 0.0
    message_items: List[MessageItemResponse] = []

    class Config:
        from_attributes = True 