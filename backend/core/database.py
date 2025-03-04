from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

from .config import get_settings
import sqlalchemy.dialects.sqlite
import aiosqlite

# 强制声明依赖关系
__all__ = ['sqlalchemy', 'aiosqlite']

def get_database_url():
    """获取数据库URL"""
    settings = get_settings()
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境，使用相对于可执行文件的路径
        base_dir = os.path.dirname(sys.executable)
        db_path = os.path.join(base_dir, 'maoflow.db')
        return f"sqlite+aiosqlite:///{db_path}"
    return settings.DATABASE_URL

settings = get_settings()
print("Settings loaded:", settings.dict())
database_url = get_database_url()
print("Database URL:", database_url)

try:
    engine = create_async_engine(database_url, echo=settings.SQL_ECHO)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
except Exception as e:
    print("Error creating database engine:", str(e))
    raise

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