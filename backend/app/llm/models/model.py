from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Enum, JSON, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.security import encrypt_text, decrypt_text

from core.base_model import Base

class LLMModel(Base):
    """LLM模型配置"""
    __tablename__ = "llm_model"  # 显式指定表名

    # 基本信息
    name: Mapped[str] = mapped_column(String(100))  # 显示名称
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 模型配置
    type: Mapped[str] = mapped_column(String(50))  # open_ai_like, anthropic, local等
    model_name: Mapped[str] = mapped_column(String(100))  # 实际调用的模型名称
    _api_key: Mapped[str] = mapped_column("api_key", Text)  # 存储加密后的API密钥
    _api_key_iv: Mapped[str] = mapped_column(String(32))  # 存储IV
    base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    @property
    def api_key(self) -> str:
        """获取解密后的API密钥"""
        if not self._api_key:
            return ""
        return decrypt_text(self._api_key, self._api_key_iv)

    @api_key.setter
    def api_key(self, value: str) -> None:
        """设置并加密API密钥"""
        if not value:
            self._api_key = ""
            self._api_key_iv = ""
            return
        self._api_key, self._api_key_iv = encrypt_text(value)

    # 模型参数默认值
    default_temperature: Mapped[float] = mapped_column(default=0.7)
    default_max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    default_system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)  # 优先级，用于排序

    # 统计和限制
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    daily_token_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # 元数据
    meta_info: Mapped[dict] = mapped_column(
        JSON,
        default=lambda: {"capabilities": [], "custom_settings": {}}
    )
