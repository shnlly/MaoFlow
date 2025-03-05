from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
import sys
import alembic.config
import alembic.command
import logging
import datetime

from .config import settings

# 强制声明依赖关系
__all__ = ['sqlalchemy', 'aiosqlite']

# 设置日志
def setup_logging():
    """设置日志"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境
        base_dir = os.path.dirname(sys.executable)
        if 'Resources' in base_dir:
            log_dir = os.path.join(os.path.dirname(base_dir), 'backend', 'logs')
        else:
            log_dir = os.path.join(base_dir, 'logs')
    else:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名（使用当前时间）
    current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'maoflow_{current_time}.log')
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return log_file

# 设置日志
log_file = setup_logging()
logger = logging.getLogger(__name__)

# 创建异步数据库引擎
engine = create_async_engine(
    settings.SQLITE_URL,
    echo=settings.SQL_ECHO,
)

# 创建异步会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 创建基础模型类
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

def run_migrations():
    """运行数据库迁移"""
    try:
        logger.info("\n=== 开始数据库迁移 ===")
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger.info(f"项目根目录: {project_root}")
        
        # 设置 alembic.ini 路径
        alembic_ini_path = os.path.join(project_root, 'alembic.ini')
        logger.info(f"Alembic配置文件路径: {alembic_ini_path}")
        
        if not os.path.exists(alembic_ini_path):
            logger.warning(f"警告: 未找到alembic.ini文件，路径: {alembic_ini_path}")
            return False
            
        # 创建 Alembic 配置
        alembic_cfg = alembic.config.Config(alembic_ini_path)
        
        # 设置迁移脚本的路径
        script_location = os.path.join(project_root, 'alembic')
        alembic_cfg.set_main_option('script_location', script_location)
        
        # 设置数据库 URL
        db_url = settings.SQLITE_URL.replace('sqlite+aiosqlite://', 'sqlite://')
        alembic_cfg.set_main_option('sqlalchemy.url', db_url)
        
        # 确保数据库目录存在
        if settings.DB_PATH:
            db_dir = os.path.dirname(settings.DB_PATH)
            os.makedirs(db_dir, exist_ok=True)
        
        # 运行迁移
        logger.info("执行数据库升级...")
        alembic.command.upgrade(alembic_cfg, "head")
        logger.info("=== 数据库迁移完成 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"\n数据库迁移过程中出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False