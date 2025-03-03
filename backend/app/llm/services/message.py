from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.models.message import Message
from app.llm.schemas.message import MessageCreate, MessageResponse

class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, message: MessageCreate) -> Message:
        db_message = Message(**message.model_dump())
        self.db.add(db_message)
        await self.db.commit()
        await self.db.refresh(db_message)
        return db_message

    async def get_message(self, message_id: str) -> Optional[Message]:
        result = await self.db.execute(
            select(Message).filter(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_conversation_messages(
        self, conversation_id: str
    ) -> List[Message]:
        result = await self.db.execute(
            select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def update_message_stats(
        self, 
        message_id: str, 
        tokens: int = 0,
        processing_time: float = 0.0
    ) -> Optional[Message]:
        message = await self.get_message(message_id)
        if message:
            message.tokens = tokens
            message.processing_time = processing_time
            await self.db.commit()
            await self.db.refresh(message)
        return message

    async def delete_message(self, message_id: str) -> bool:
        message = await self.get_message(message_id)
        if message:
            await self.db.delete(message)
            await self.db.commit()
            return True
        return False 