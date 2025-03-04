from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import sys

def get_env_file():
    """获取环境文件路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境
        base_dir = os.path.dirname(sys.executable)
        env_file = os.path.join(base_dir, '.env.prod')
    else:
        # 开发环境
        env_file = '.env.development'
    return env_file

class Settings(BaseSettings):
    @property
    def docs_enabled(self):
        return self.DEBUG

    """应用配置类"""
    # 基础配置
    APP_NAME: str = "MaoFlow"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    API_V1_STR: str = "/api/v1"
    HOST: str = "localhost"
    PORT: int = 17349
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./maoflow.db"
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

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding='utf-8',
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings()
