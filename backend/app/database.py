from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# SQLite URL 和引擎配置
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./maoflow.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    """获取数据库会话的依赖函数"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 