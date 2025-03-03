from typing import Generator, Optional
from openai import AsyncOpenAI
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import get_settings
from ..models.model import LLMModel

settings = get_settings()

def create_llm_client(model_config: LLMModel) -> AsyncOpenAI:
    """
    根据模型配置创建LLM客户端
    
    Args:
        model_config: LLM模型配置
        
    Returns:
        AsyncOpenAI: OpenAI客户端实例
    """
    return AsyncOpenAI(
        api_key=model_config.api_key,
        base_url=model_config.base_url or os.getenv('DEFAULT_BASE_URI'),
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def create_chat_completion(
    messages: list,
    model_config: Optional[LLMModel] = None,
    temperature: Optional[float] = None,
    stream: bool = True
) -> Generator[dict, None, None]:
    """
    创建聊天完成并支持流式输出
    
    Args:
        messages: 消息列表
        model_config: LLM模型配置，如果为None则使用默认配置
        temperature: 温度参数，如果为None则使用模型默认值
        stream: 是否使用流式输出
        
    Yields:
        Dict[str, Any]: 包含类型和内容的字典
    """
    try:
        # 如果没有提供模型配置，使用默认配置
        if model_config is None:
            client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_API_BASE,
            )
            model_name = settings.DEFAULT_MODEL
            temperature = temperature or 0.7
        else:
            client = create_llm_client(model_config)
            model_name = model_config.model_name
            temperature = temperature or model_config.default_temperature
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            } for msg in messages],
            temperature=temperature,
            stream=stream
        )
        
        if stream:
            async for chunk in response:
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