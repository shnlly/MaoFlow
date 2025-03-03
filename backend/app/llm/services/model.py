from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from core.exceptions import NotFoundException, ValidationError
from ..schemas.model import LLMModelCreate, LLMModelUpdate
from ..models import Conversation, Message, LLMModel

class LLMModelService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _validate_model_data(self, data: dict) -> None:
        """验证模型数据"""
        # 检查类型是否有效
        valid_types = ["open_ai_like", "anthropic", "local", "azure", "claude"]
        if data.get("type") and data["type"] not in valid_types:
            raise ValidationError(f"Invalid model type. Must be one of: {', '.join(valid_types)}")
        
        # 检查温度值是否在有效范围内
        if "default_temperature" in data:
            temp = data["default_temperature"]
            if temp is not None and (temp < 0 or temp > 2):
                raise ValidationError("Temperature must be between 0 and 2")
        
        # 检查base_url格式（如果提供）
        if data.get("base_url"):
            if not data["base_url"].startswith(("http://", "https://")):
                raise ValidationError("base_url must start with http:// or https://")

    async def create(self, data: LLMModelCreate) -> LLMModel:
        # 验证数据
        await self._validate_model_data(data.model_dump())
        
        # 创建模型
        model = LLMModel(**data.model_dump())
        self.session.add(model)
        await self.session.commit()
        return model

    async def get(self, model_id: str) -> Optional[LLMModel]:
        result = await self.session.get(LLMModel, model_id)
        if not result:
            raise NotFoundException(f"Model {model_id} not found")
        return result

    async def list(self, skip: int = 0, limit: int = 10, 
                  type: Optional[str] = None,
                  is_active: Optional[bool] = None) -> Tuple[List[LLMModel], int]:
        query = select(LLMModel)
        
        if type:
            query = query.filter(LLMModel.type == type)
        if is_active is not None:
            query = query.filter(LLMModel.is_active == is_active)
            
        # 获取总数
        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )
        
        # 获取分页数据
        query = query.order_by(LLMModel.priority.desc(), LLMModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        return list(models), total

    async def update(self, model_id: str, data: LLMModelUpdate) -> LLMModel:
        model = await self.get(model_id)
        
        # 验证更新数据
        update_data = data.model_dump(exclude_unset=True)
        await self._validate_model_data(update_data)
        
        # 更新模型
        for key, value in update_data.items():
            setattr(model, key, value)
            
        await self.session.commit()
        return model

    async def delete(self, model_id: str) -> None:
        model = await self.get(model_id)
        # 检查是否有关联的会话
        conversation_count = await self.session.scalar(
            select(func.count()).select_from(
                select(LLMModel)
                .join(LLMModel.conversations)
                .filter(LLMModel.id == model_id)
                .subquery()
            )
        )
        if conversation_count > 0:
            raise ValidationError(f"Cannot delete model {model_id} as it has {conversation_count} associated conversations")
        
        await self.session.delete(model)
        await self.session.commit()

    async def update_token_usage(self, model_id: str, tokens: int) -> None:
        model = await self.get(model_id)
        
        # 检查是否超过每日限制
        if model.daily_token_limit:
            # 获取今日使用量
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = today_start + timedelta(days=1)
            
            # 计算今日使用量
            today_usage = await self.get_today_token_usage(model_id, today_start, today_end)
            
            # 检查是否会超过限制
            if today_usage + tokens > model.daily_token_limit:
                raise ValidationError(f"Daily token limit ({model.daily_token_limit}) exceeded")
        
        model.total_tokens_used += tokens
        await self.session.commit()

    async def get_today_token_usage(self, model_id: str, 
                                  start_time: datetime, 
                                  end_time: datetime) -> int:
        """获取指定时间范围内的token使用量"""

        
        result = await self.session.scalar(
            select(func.sum(Message.tokens))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Conversation.model_id == model_id,
                Message.created_at >= start_time,
                Message.created_at < end_time
            )
        )
        return result or 0
