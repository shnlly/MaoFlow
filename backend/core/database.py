from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL, echo=settings.SQL_ECHO)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_session() -> AsyncSession:
    """获取数据库会话实例"""
    async with async_session() as session:
        try:
            return session
        finally:
            await session.close()