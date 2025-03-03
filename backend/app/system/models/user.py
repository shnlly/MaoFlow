from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, Integer, JSON, DateTime, select, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_model import Base

class User(Base):
    """用户模型"""
    __tablename__ = "sys_user"  # 添加表名前缀，表明这是系统用户表
    
    # 基本信息
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 用户设置
    settings: Mapped[dict] = mapped_column(
        JSON, 
        default=lambda: {
            "theme": "light",
            "language": "zh-CN",
            "notifications_enabled": True,
            "custom_settings": {
                "font_size": 14,
                "color": "blue"
            }
        }
    )
    
    # 使用统计
    conversation_count: Mapped[int] = mapped_column(Integer, default=0)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # 开发测试用
    is_test_user: Mapped[bool] = mapped_column(Boolean, default=False)

    @classmethod
    async def get_or_create_test_user(cls, db: AsyncSession) -> "User":
        """获取或创建测试用户"""
        stmt = select(cls).filter_by(is_test_user=True)
        result = await db.execute(stmt)
        test_user = result.scalar_one_or_none()
        
        if not test_user:
            test_user = cls(
                username="test_user",
                email="test@example.com",
                full_name="测试用户",
                is_test_user=True,
                settings={
                    "theme": "light",
                    "language": "zh-CN",
                    "notifications_enabled": True,
                    "custom_settings": {
                        "font_size": 14,
                        "color": "blue"
                    }
                }
            )
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
        return test_user

    def update_activity(self) -> None:
        """更新用户活动时间"""
        self.last_active_at = datetime.utcnow()

    def update_conversation_stats(self, messages_count: int = 0, tokens: int = 0) -> None:
        """更新会话统计信息"""
        if messages_count > 0:
            self.conversation_count += 1
            self.message_count += messages_count
        if tokens > 0:
            self.total_tokens += tokens
        self.update_activity()

    def update_settings(self, settings: dict) -> None:
        """更新用户设置"""
        if not self.settings:
            self.settings = {}
        self.settings.update(settings)

    @classmethod
    async def get_system_stats(cls, db: AsyncSession) -> dict:
        """获取系统用户统计信息"""
        total_users = await db.scalar(select(func.count(cls.id)))
        active_users = await db.scalar(
            select(func.count(cls.id)).filter(cls.is_active == True)
        )
        total_conversations = await db.scalar(
            select(func.sum(cls.conversation_count))
        )
        total_messages = await db.scalar(
            select(func.sum(cls.message_count))
        )
        total_tokens = await db.scalar(
            select(func.sum(cls.total_tokens))
        )
        
        return {
            "total_users": total_users or 0,
            "active_users": active_users or 0,
            "total_conversations": total_conversations or 0,
            "total_messages": total_messages or 0,
            "total_tokens": total_tokens or 0
        } 