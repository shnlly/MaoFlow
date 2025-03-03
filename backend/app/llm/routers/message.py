from typing import List, Optional, AsyncGenerator
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid

from core.database import get_db
from ..services import MessageService, ConversationService
from ..schemas.message import (
    MessageCreate,
    MessageResponse
)
from ..schemas.message_item import MessageItemCreate
from ..services.llm_service import create_chat_completion
from ..models.message import MessageRole, MessageType

router = APIRouter(prefix="/messages", tags=["消息管理"])

def json_dumps_unicode(obj):
    return json.dumps(obj, ensure_ascii=False)

# 消息相关路由
@router.post("", response_model=MessageResponse)
async def create_message(
    data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新消息并支持流式输出"""
    message_service = MessageService(db)
    conversation_service = ConversationService(db)
    
    # 获取会话信息
    conversation = await conversation_service.get_conversation(data.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 生成消息ID
    message_id = str(uuid.uuid4())
    
    # 创建助手消息
    assistant_message = MessageCreate(
        conversation_id=data.conversation_id,
        user_id=data.user_id,
        role=MessageRole.ASSISTANT
    )
    message = await message_service.create_message(assistant_message)
    
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            # 构建消息列表
            messages = [{
                "role": MessageRole.USER.value,
                "content": "",
                "conversation_id": data.conversation_id,
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
                    
                    # 流式返回给客户端
                    yield f"data: {json_dumps_unicode(chunk)}\n\n"
            
            # 存储各类型的消息内容
            for item_type, contents in collected_contents.items():
                if contents:
                    item_data = MessageItemCreate(
                        message_id=message_id,
                        conversation_id=data.conversation_id,
                        content="".join(contents),
                        type=item_type
                    )
                    await message_service.create_message_item(item_data)
            
            # 更新会话的最后消息时间
            await conversation_service.update_conversation_last_message(data.conversation_id)
            
            yield "data: [DONE]\n\n"
                    
        except Exception as e:
            error_message = f"发生错误: {str(e)}"
            yield f"data: {json_dumps_unicode({'type': 'error', 'content': error_message})}\n\n"
            yield "data: [DONE]\n\n"

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
