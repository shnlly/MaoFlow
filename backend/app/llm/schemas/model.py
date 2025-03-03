from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class LLMModelBase(BaseModel):
    name: str = Field(..., description="模型显示名称")
    description: Optional[str] = Field(None, description="模型描述")
    type: str = Field(..., description="模型类型，如 open_ai_like, anthropic, local 等")
    model_name: str = Field(..., description="实际调用的模型名称")
    api_key: str = Field(..., description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    default_temperature: float = Field(0.7, description="默认温度")
    default_max_tokens: Optional[int] = Field(None, description="默认最大token数")
    default_system_prompt: Optional[str] = Field(None, description="默认系统提示词")
    priority: int = Field(0, description="优先级")
    daily_token_limit: Optional[int] = Field(None, description="每日token限制")
    meta_info: Dict = Field(default_factory=lambda: {"capabilities": [], "custom_settings": {}})
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class LLMModelCreate(BaseModel):
    name: str = Field(..., description="模型显示名称")
    description: Optional[str] = Field(None, description="模型描述")
    type: str = Field("open_ai_like", description="模型类型，如 open_ai_like, anthropic, local 等")
    model_name: str = Field(..., description="实际调用的模型名称")
    api_key: str = Field(..., description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")

class LLMModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_temperature: Optional[float] = None
    default_max_tokens: Optional[int] = None
    default_system_prompt: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    daily_token_limit: Optional[int] = None
    meta_info: Optional[Dict] = None
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class LLMModelInDB(LLMModelBase):
    id: str
    is_active: bool
    total_tokens_used: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class LLMModelList(BaseModel):
    total: int
    items: List[LLMModelInDB]
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=()) 