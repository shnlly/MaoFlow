from typing import Optional
from pydantic import BaseModel

class MessageItemBase(BaseModel):
    content: str
    type: str
    meta_info: Optional[dict] = {}

class MessageItemCreate(MessageItemBase):
    message_id: str

class MessageItemResponse(MessageItemBase):
    id: str
    message_id: str

    class Config:
        from_attributes = True 