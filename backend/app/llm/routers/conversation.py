from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from ..services import ConversationService
from ..schemas import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse
)

router = APIRouter(prefix="/conversations", tags=["对话管理"])

# 会话相关路由
@router.post("", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新会话"""
    conversation_service = ConversationService(db)
    return await conversation_service.create_conversation(data)

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会话详情"""
    conversation_service = ConversationService(db)
    return await conversation_service.get_conversation(conversation_id)

@router.get("/user/{user_id}", response_model=List[ConversationResponse])
async def list_user_conversations(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取用户的会话列表"""
    conversation_service = ConversationService(db)
    return await conversation_service.list_user_conversations(
        user_id=user_id,
        skip=skip,
        limit=limit,
        status=status
    )

@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新会话信息"""
    conversation_service = ConversationService(db)
    return await conversation_service.update_conversation(conversation_id, data)

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除会话"""
    conversation_service = ConversationService(db)
    await conversation_service.delete_conversation(conversation_id)
    return {"message": "会话已删除"}
