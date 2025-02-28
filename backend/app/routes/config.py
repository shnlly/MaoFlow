from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from ..database import get_db
from ..models import UserConfig
from ..schemas.config import UserConfigCreate, UserConfigUpdate, UserConfigResponse

router = APIRouter(prefix="/config", tags=["配置管理"])

@router.post("/user", response_model=UserConfigResponse)
async def create_user_config(config: UserConfigCreate, db: AsyncSession = Depends(get_db)):
    """创建用户配置"""
    db_config = UserConfig(**config.model_dump())
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config

@router.get("/user/{user_id}", response_model=UserConfigResponse)
async def get_user_config(user_id: str, db: AsyncSession = Depends(get_db)):
    """获取用户配置"""
    result = await db.execute(select(UserConfig).filter(UserConfig.user_id == user_id))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="用户配置不存在")
    return config

@router.put("/user/{user_id}", response_model=UserConfigResponse)
async def update_user_config(
    user_id: str, config: UserConfigUpdate, db: AsyncSession = Depends(get_db)
):
    """更新用户配置"""
    result = await db.execute(select(UserConfig).filter(UserConfig.user_id == user_id))
    db_config = result.scalar_one_or_none()
    if not db_config:
        raise HTTPException(status_code=404, detail="用户配置不存在")
    
    update_data = config.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_config, key, value)
    
    await db.commit()
    await db.refresh(db_config)
    return db_config

@router.delete("/user/{user_id}")
async def delete_user_config(user_id: str, db: AsyncSession = Depends(get_db)):
    """删除用户配置"""
    result = await db.execute(select(UserConfig).filter(UserConfig.user_id == user_id))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="用户配置不存在")
    
    await db.delete(config)
    await db.commit()
    return {"message": "配置已删除"} 