from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from ..services.user_service import UserService
from ..schemas.user import UserResponse

router = APIRouter(prefix="/user", tags=["users"])

@router.get("/test-user", response_model=UserResponse)
async def get_test_user(
    session: AsyncSession = Depends(get_session)
):
    """获取或创建测试用户"""
    service = UserService(session)
    return await service.get_test_user()

@router.get("/{user_id}/settings", response_model=Dict[str, Any])
async def get_user_settings(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """获取用户配置信息"""
    service = UserService(session)
    try:
        return await service.get_user_settings(user_id)
    except HTTPException as e:
        raise e

@router.put("/{user_id}/settings", response_model=Dict[str, Any])
async def update_user_settings(
    user_id: str,
    settings: Dict[str, Any],
    session: AsyncSession = Depends(get_session)
):
    """更新用户配置信息"""
    service = UserService(session)
    try:
        return await service.update_user_settings(user_id, settings)
    except HTTPException as e:
        raise e 