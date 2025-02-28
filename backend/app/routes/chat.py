from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import os
from openai import OpenAI
from typing import AsyncGenerator, Optional, Generator
from dotenv import load_dotenv
import pathlib

router = APIRouter()

# 加载环境变量
env_path = pathlib.Path(__file__).parents[2] / '.env.development'
load_dotenv(env_path)

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv('DEFAULT_API_KEY'),
    base_url=os.getenv('DEFAULT_BASE_URI'),
)

def json_dumps_unicode(obj):
    return json.dumps(obj, ensure_ascii=False)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def create_chat_completion(
    messages: list,
    model: str = None,
    temperature: float = 0.7,
    stream: bool = True
) -> Generator[dict, None, None]:
    try:
        response = client.chat.completions.create(
            model=model or os.getenv('DEFAULT_MODEL_NAME'),
            messages=messages,
            temperature=temperature,
            stream=stream
        )
        
        if stream:
            for chunk in response:
                if chunk and chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    # 处理推理内容
                    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                        yield {
                            "type": "think",
                            "content": delta.reasoning_content
                        }
                    # 处理最终内容
                    elif hasattr(delta, "content") and delta.content:
                        yield {
                            "type": "message",
                            "content": delta.content
                        }
        else:
            if response.choices and response.choices[0].message:
                yield {
                    "type": "message",
                    "content": response.choices[0].message.content
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/chat")
async def chat(query: str):
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            # 构建消息列表
            messages = [{"role": "user", "content": query}]
            
            # 调用 API 并流式返回结果
            for chunk in create_chat_completion(messages):
                if chunk:
                    yield f"data: {json_dumps_unicode(chunk)}\n\n"
            
            # 发送结束标记
            yield "data: [DONE]\n\n"
                    
        except Exception as e:
            error_message = f"发生错误: {str(e)}"
            yield f"data: {json_dumps_unicode({'type': 'message', 'content': error_message})}\n\n"
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