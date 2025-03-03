from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.exceptions import ValidationError, NotFoundException
from ..services.model import LLMModelService
from ..schemas.model import (
    LLMModelCreate,
    LLMModelUpdate,
    LLMModelInDB,
    LLMModelList
)

router = APIRouter(prefix="/models", tags=["模型管理"])

@router.post("", response_model=LLMModelInDB)
async def create_model(
    data: LLMModelCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建新的LLM模型配置"""
    try:
        service = LLMModelService(session)
        return await service.create(data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=LLMModelList)
async def list_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    type: Optional[str] = None,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取LLM模型列表"""
    try:
        service = LLMModelService(session)
        models, total = await service.list(skip, limit, type, is_active)
        return LLMModelList(total=total, items=models)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{model_id}", response_model=LLMModelInDB)
async def update_model(
    model_id: str,
    data: LLMModelUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新LLM模型配置"""
    try:
        service = LLMModelService(session)
        return await service.update(model_id, data)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除LLM模型配置"""
    try:
        service = LLMModelService(session)
        await service.delete(model_id)
        return {"message": "Model deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 