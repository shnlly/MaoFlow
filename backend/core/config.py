from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """应用配置类"""
    # 基础配置
    APP_NAME: str = "MaoFlow"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    SQL_ECHO: bool = False
    
    # 安全配置
    SECRET_KEY: str = "sxai123456"
    ENCRYPTION_KEY: Optional[str] = None  # 用于加密敏感数据，如果不设置则使用SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # CORS配置
    CORS_ORIGINS: list[str] = ["*"]
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    DEFAULT_MODEL: str = "gpt-3.5-turbo"


    class Config:
        env_file = ".env.development"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings() 