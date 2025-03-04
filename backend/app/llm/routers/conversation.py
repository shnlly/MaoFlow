from typing import List, Optional, AsyncGenerator
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid

from core.database import get_db
from ..services import ConversationService, MessageService
from ..schemas import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageCreate,
    MessageResponse
)
from ..schemas.message_item import MessageItemCreate, MessageItemResponse
from ..services.llm_service import create_chat_completion
from ..models.message import MessageRole, MessageType

router = APIRouter(prefix="/conversations", tags=["对话管理"])

def json_dumps_unicode(obj):
    return json.dumps(obj, ensure_ascii=False)

def clean_text(text: str) -> str:
    """清理文本，去除多余的换行符和空白字符"""
    # 去除首尾的空白字符
    text = text.strip()
    # 将多个连续的换行符替换为单个换行符
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    return text

# 会话相关路由
@router.post("", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新会话"""
    conversation_service = ConversationService(db)
    return await conversation_service.create_conversation(data)

@router.post("/{conversation_id}/query")
async def query_conversation(
    conversation_id: str,
    query: str,
    db: AsyncSession = Depends(get_db)
):
    """发送查询到会话"""
    message_service = MessageService(db)
    conversation_service = ConversationService(db)
    
    # 获取会话信息
    conversation = await conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 生成消息ID
    message_id = str(uuid.uuid4())
    
    # 创建用户消息
    user_message = MessageCreate(
        conversation_id=conversation_id,
        user_id=conversation.user_id,
        content=query,
        role=MessageRole.USER
    )
    user_message_obj = await message_service.create_message(user_message)
    
    # 为用户消息创建message_item
    user_item_data = MessageItemCreate(
        message_id=user_message_obj.id,
        conversation_id=conversation_id,
        content=clean_text(query),
        type="message"
    )
    await message_service.create_message_item(user_item_data)
    
    # 创建助手消息
    assistant_message = MessageCreate(
        conversation_id=conversation_id,
        user_id=conversation.user_id,
        role=MessageRole.ASSISTANT
    )
    assistant_message_obj = await message_service.create_message(assistant_message)
    
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            # 构建消息列表
            messages = [{
                "role": MessageRole.USER.value,
                "content": query,
                "conversation_id": conversation_id,
                "message_id": message_id,
                "type": MessageType.TEXT.value
            }]
            
            # 用于收集不同类型的消息内容
            collected_contents = {
                "think": [],
                "message": [],
                "action": [],
                "observation": []
            }
            
            # 调用LLM服务并流式返回结果
            async for chunk in create_chat_completion(
                messages=messages,
                model_config=conversation.model,  # 使用会话绑定的模型
                stream=True
            ):
                if chunk:
                    # 收集对应类型的内容
                    chunk_type = chunk.get("type", "message")
                    chunk_content = chunk.get("content", "")
                    if chunk_type in collected_contents:
                        collected_contents[chunk_type].append(chunk_content)
                    
                    # 构建完整的消息块
                    message_block = {
                        "type": chunk_type,
                        "content": chunk_content,
                        "conversation_id": conversation_id,
                        "message_id": message_id
                    }
                    
                    # 流式返回给客户端
                    yield f"data: {json_dumps_unicode(message_block)}\n\n"
            
            # 存储各类型的消息内容
            for item_type, contents in collected_contents.items():
                if contents:
                    # 对于 message 类型，更新助手消息的内容
                    if item_type == "message":
                        # 重新获取消息对象以确保它在当前会话中
                        current_message = await message_service.get_message(assistant_message_obj.id)
                        if current_message:
                            current_message.content = clean_text("".join(contents))
                            await message_service.update_message(current_message)
                    
                    # 存储消息项，使用assistant_message_obj.id作为message_id
                    item_data = MessageItemCreate(
                        message_id=assistant_message_obj.id,  # 使用助手消息的ID
                        conversation_id=conversation_id,
                        content=clean_text("".join(contents)),
                        type=item_type
                    )
                    await message_service.create_message_item(item_data)
            
            # 更新会话的最后消息时间
            await conversation_service.update_conversation_last_message(conversation_id)
            
            # 发送完成消息
            yield f"data: {json_dumps_unicode({'type': 'done', 'conversation_id': conversation_id, 'message_id': message_id})}\n\n"
                    
        except Exception as e:
            error_message = f"发生错误: {str(e)}"
            yield f"data: {json_dumps_unicode({'type': 'error', 'content': error_message, 'conversation_id': conversation_id, 'message_id': message_id})}\n\n"
            yield f"data: {json_dumps_unicode({'type': 'done', 'conversation_id': conversation_id, 'message_id': message_id})}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream; charset=utf-8",
            "X-Accel-Buffering": "no"
        }
    )

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

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会话的历史消息列表"""
    message_service = MessageService(db)
    return await message_service.get_conversation_messages_with_items(conversation_id)
