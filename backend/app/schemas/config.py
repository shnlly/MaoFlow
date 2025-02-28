from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class UserConfigBase(BaseModel):
    """用户配置基础模型"""
    api_key: str
    base_url: str = Field(default="https://api.openai.com/v1")
    ai_model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2000, ge=1)
    
    model_config = ConfigDict(from_attributes=True)

class UserConfigCreate(UserConfigBase):
    """创建用户配置的请求模型"""
    user_id: str

class UserConfigUpdate(BaseModel):
    """更新用户配置的请求模型"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    ai_model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    
    model_config = ConfigDict(from_attributes=True)

class UserConfigResponse(UserConfigBase):
    """用户配置的响应模型"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime 