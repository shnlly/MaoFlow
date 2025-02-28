from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Conversation, Message
from ..schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageCreate,
    MessageResponse
)

router = APIRouter(prefix="/conversations", tags=["会话管理"])

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate, db: AsyncSession = Depends(get_db)
):
    """创建新会话"""
    db_conversation = Conversation(**conversation.model_dump())
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)
    # 手动加载消息列表
    await db.refresh(db_conversation, ["messages"])
    return ConversationResponse.from_orm(db_conversation)

@router.get("/{user_id}", response_model=List[ConversationResponse])
async def list_conversations(user_id: str, db: AsyncSession = Depends(get_db)):
    """获取用户的所有会话"""
    result = await db.execute(
        select(Conversation)
        .filter(Conversation.user_id == user_id)
        .options(selectinload(Conversation.messages))
    )
    conversations = result.scalars().all()
    return [ConversationResponse.from_orm(conv) for conv in conversations]

@router.get("/{conversation_id}/detail", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """获取会话详情"""
    result = await db.execute(
        select(Conversation)
        .filter(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    return ConversationResponse.from_orm(conversation)

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: int, message: MessageCreate, db: AsyncSession = Depends(get_db)
):
    """添加消息到会话"""
    # 检查会话是否存在
    result = await db.execute(
        select(Conversation)
        .filter(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 创建新消息
    db_message = Message(conversation_id=conversation_id, **message.model_dump())
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """删除会话"""
    result = await db.execute(select(Conversation).filter(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    await db.delete(conversation)
    await db.commit()
    return {"message": "会话已删除"} 