from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..models import Conversation, Message, MessageItem
from ..schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
    MessageItemCreate
)

class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(self, data: ConversationCreate) -> Conversation:
        """创建新会话"""
        conversation = Conversation(**data.model_dump())
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation(self, conversation_id: str) -> Conversation:
        """获取会话详情"""
        stmt = select(Conversation).filter(Conversation.id == conversation_id)
        result = await self.db.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return conversation

    async def list_user_conversations(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[Conversation]:
        """获取用户的会话列表"""
        query = select(Conversation).filter(Conversation.user_id == user_id)
        
        if status:
            query = query.filter(Conversation.status == status)
        
        query = query.order_by(Conversation.updated_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_conversation(
        self,
        conversation_id: str,
        data: ConversationUpdate
    ) -> Conversation:
        """更新会话信息"""
        conversation = await self.get_conversation(conversation_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(conversation, key, value)
        
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def delete_conversation(self, conversation_id: str) -> None:
        """删除会话（软删除）"""
        conversation = await self.get_conversation(conversation_id)
        conversation.soft_delete()
        await self.db.commit()

    async def update_conversation_last_message(self, conversation_id: str) -> None:
        """更新会话的最后消息时间"""
        conversation = await self.get_conversation(conversation_id)
        conversation.last_message_at = datetime.utcnow()
        await self.db.commit()

class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, data: MessageCreate) -> Message:
        """创建新消息"""
        message = Message(**data.model_dump())
        self.db.add(message)
        
        # 更新会话统计信息
        stmt = select(Conversation).filter(Conversation.id == data.conversation_id)
        result = await self.db.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if conversation:
            conversation.update_stats(messages_count=1, tokens=message.tokens)
        
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def list_conversation_messages(
        self,
        conversation_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Message]:
        """获取会话的消息列表"""
        query = select(Message).filter(Message.conversation_id == conversation_id)
        query = query.order_by(Message.created_at)
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

class ThoughtService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_thought(self, data: MessageItemCreate) -> MessageItem:
        """创建消息区块节点"""
        thought = MessageItem(**data.model_dump())
        self.db.add(thought)
        await self.db.commit()
        await self.db.refresh(thought)
        return thought

    async def list_message_thoughts(
        self,
        message_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[MessageItem]:
        """获取消息的消息区块列表"""
        query = select(MessageItem).filter(MessageItem.message_id == message_id)
        query = query.order_by(MessageItem.order)
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all() 