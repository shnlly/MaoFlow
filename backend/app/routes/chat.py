from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import json
import asyncio
from ..config.settings import get_settings, Settings
from typing import AsyncGenerator
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

router = APIRouter()

def create_stream_chunk(type: str | None, content: str) -> str:
    """创建流式响应的数据块"""
    data = {"content": content}
    if type:
        data["type"] = type
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

async def create_chat_completion(query: str, api_key: str, model_name: str, base_uri: str):
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_uri,
        timeout=httpx.Timeout(connect=5.0, read=300.0, write=300.0, pool=300.0)
    )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_chat_response():
        return await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": query}],
            stream=True
        )

    try:
        async def generate():
            try:
                response = await get_chat_response()

                think_buffer = ""
                message_buffer = ""
                current_type = None
                
                async for chunk in response:
                    if not chunk.choices[0].delta:
                        continue
                    
                    try:
                        # 处理思考内容
                        if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                            if current_type != "think":
                                current_type = "think"
                                think_buffer = ""
                            think_buffer += chunk.choices[0].delta.reasoning_content
                            yield create_stream_chunk("think", think_buffer)
                        
                        # 处理正文内容
                        elif hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                            if current_type != "message":
                                current_type = "message"
                                message_buffer = ""
                            message_buffer += chunk.choices[0].delta.content
                            yield create_stream_chunk("message", message_buffer)
                    except Exception as chunk_error:
                        print(f"处理数据块时出错: {str(chunk_error)}")
                        continue

                # 确保最后一个消息被发送
                if message_buffer:
                    yield create_stream_chunk("message", message_buffer)
                elif think_buffer:
                    yield create_stream_chunk("think", think_buffer)

            except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                yield create_stream_chunk("message", f"请求超时，请重试。错误信息：{str(e)}")
            except httpx.RemoteProtocolError as e:
                yield create_stream_chunk("message", "连接中断，请重试。")
            except Exception as e:
                yield create_stream_chunk("message", f"发生错误：{str(e)}")
            finally:
                # 确保流正常结束
                yield "data: [DONE]\n\n"

        return generate()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat")
async def chat(
    query: str,
    settings: Settings = Depends(get_settings)
) -> StreamingResponse:
    api_key = settings.DEFAULT_API_KEY
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")

    model_name = settings.DEFAULT_MODEL_NAME
    base_uri = settings.DEFAULT_BASE_URI

    try:
        generator = await create_chat_completion(query, api_key, model_name, base_uri)
        
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/test")
async def chat_test() -> StreamingResponse:
    """测试接口，用于前端开发测试"""
    async def generate_test_messages():
        # 模拟思考过程
        think_content = ""
        for thought in ["让我思考一下这个问题...\n", 
                       "这个问题涉及到几个关键点：\n",
                       "1. 性能优化\n2. 用户体验\n3. 代码质量"]:
            think_content += thought
            yield create_stream_chunk("think", think_content)
            await asyncio.sleep(0.5)
        
        # 模拟工具使用
        yield create_stream_chunk("tool", "正在分析代码结构...")
        await asyncio.sleep(1)
        
        # 模拟正文回答
        message_content = ""
        response = """基于上述分析，我建议从以下几个方面进行改进：

1. 性能优化
- 减少不必要的重渲染
- 优化数据流转过程
- 实现合理的缓存策略

2. 用户体验
- 添加加载状态提示
- 优化错误处理机制
- 提供更清晰的反馈

3. 代码质量
- 遵循最佳实践
- 添加完整的测试
- 优化代码结构"""

        for line in response.split('\n'):
            message_content += line + '\n'
            if line.strip():
                yield create_stream_chunk("message", message_content)
                await asyncio.sleep(0.2)
        
    return StreamingResponse(
        generate_test_messages(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    ) 