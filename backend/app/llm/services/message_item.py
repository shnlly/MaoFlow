from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.models.message_item import MessageItem
from app.llm.schemas.message_item import MessageItemCreate

class MessageItemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message_item(self, item: MessageItemCreate) -> MessageItem:
        db_item = MessageItem(**item.model_dump())
        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)
        return db_item

    async def get_message_item(self, item_id: str) -> Optional[MessageItem]:
        result = await self.db.execute(
            select(MessageItem).filter(MessageItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_message_items(self, message_id: str) -> List[MessageItem]:
        result = await self.db.execute(
            select(MessageItem)
            .filter(MessageItem.message_id == message_id)
            .order_by(MessageItem.created_at)
        )
        return list(result.scalars().all())

    async def delete_message_item(self, item_id: str) -> bool:
        item = await self.get_message_item(item_id)
        if item:
            await self.db.delete(item)
            await self.db.commit()
            return True
        return False 