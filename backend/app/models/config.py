from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Config(Base):
    """用户配置模型"""
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[str] = mapped_column(String(1000))
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    
class UserConfig(Base):
    """用户个性化配置"""
    api_key: Mapped[str] = mapped_column(String(100))
    base_url: Mapped[str] = mapped_column(String(200), default="https://api.openai.com/v1")
    ai_model: Mapped[str] = mapped_column(String(50), default="gpt-3.5-turbo")
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(default=2000)
    user_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # 用于区分不同用户的配置 