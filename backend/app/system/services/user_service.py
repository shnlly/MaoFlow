from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from ..models.user import User

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_test_user(self) -> User:
        """获取或创建测试用户"""
        return await User.get_or_create_test_user(self.db)

    async def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """获取用户配置信息"""
        stmt = select(User).filter(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return user.settings

    async def update_user_settings(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户配置信息"""
        stmt = select(User).filter(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 更新设置
        current_settings = dict(user.settings)
        
        # 处理自定义设置
        if "custom_settings" in settings:
            if "custom_settings" not in current_settings:
                current_settings["custom_settings"] = {}
            current_settings["custom_settings"].update(settings["custom_settings"])
            del settings["custom_settings"]
        
        # 更新其他设置
        current_settings.update(settings)
        user.settings = current_settings
        
        await self.db.commit()
        return user.settings 