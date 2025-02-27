from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    # 服务器配置
    DEBUG: bool = False
    HOST: str = "localhost"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # AI 模型配置
    DEFAULT_API_KEY: Optional[str] = None
    DEFAULT_MODEL_NAME: str = "gpt-3.5-turbo"
    DEFAULT_BASE_URI: str = "https://api.openai.com/v1"

    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env.development")
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings() 