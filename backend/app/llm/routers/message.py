from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from ..services import MessageService
from ..schemas.message import (
    MessageCreate,
    MessageResponse
)

router = APIRouter(prefix="/messages", tags=["消息管理"])

# 消息相关路由
@router.post("", response_model=MessageResponse)
async def create_message(
    data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新消息"""
    message_service = MessageService(db)
    return await message_service.create_message(data)

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def list_conversation_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会话的消息列表"""
    message_service = MessageService(db)
    return await message_service.get_conversation_messages(
        conversation_id=conversation_id,
    )
