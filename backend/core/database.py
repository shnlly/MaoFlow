from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
import alembic.config
import alembic.command
import logging
import datetime

from .config import get_settings
import sqlalchemy.dialects.sqlite
import aiosqlite

# 强制声明依赖关系
__all__ = ['sqlalchemy', 'aiosqlite']

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

def get_database_url():
    """获取数据库URL"""
    settings = get_settings()
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境，使用相对于可执行文件的路径
        base_dir = os.path.dirname(sys.executable)
        if 'Resources' in base_dir:
            # 对于 Electron 应用，数据库文件应该在 Resources/backend 目录下
            base_dir = os.path.join(os.path.dirname(base_dir), 'backend')
        db_path = os.path.join(base_dir, 'maoflow.db')
        # 确保使用绝对路径
        db_path = os.path.abspath(db_path)
        logger.info(f"数据库路径: {db_path}")
        # 使用正斜杠替换反斜杠，确保 URL 格式正确
        db_path = db_path.replace('\\', '/')
        # 添加正确的 SQLite URL 前缀
        return f"sqlite+aiosqlite:///{db_path}"
    return settings.DATABASE_URL

settings = get_settings()
logger.info(f"Settings loaded: {settings.dict()}")
database_url = get_database_url()
logger.info(f"Database URL: {database_url}")

def get_project_root():
    """获取项目根目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境
        base_dir = os.path.dirname(sys.executable)
        # 对于 Electron 应用，需要定位到 Resources/backend 目录
        if 'Resources' in base_dir:
            return os.path.join(os.path.dirname(base_dir), 'backend')
        return base_dir
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_migrations():
    """运行数据库迁移"""
    try:
        logger.info("\n=== 开始数据库迁移 ===")
        # 获取项目根目录
        project_root = get_project_root()
        logger.info(f"项目根目录: {project_root}")
        
        # 设置 alembic.ini 路径
        alembic_ini_path = os.path.join(project_root, 'alembic.ini')
        logger.info(f"Alembic配置文件路径: {alembic_ini_path}")
        
        if not os.path.exists(alembic_ini_path):
            logger.warning(f"警告: 未找到alembic.ini文件，路径: {alembic_ini_path}")
            return False
        else:
            logger.info("成功找到 alembic.ini 文件")
            
        # 创建 Alembic 配置
        alembic_cfg = alembic.config.Config(alembic_ini_path)
        
        # 设置迁移脚本的路径
        script_location = os.path.join(project_root, 'alembic')
        logger.info(f"迁移脚本路径: {script_location}")
        
        # 检查迁移脚本目录
        if not os.path.exists(script_location):
            logger.warning(f"警告: 未找到迁移脚本目录: {script_location}")
            logger.info(f"目录 {os.path.dirname(script_location)} 的内容:")
            try:
                logger.info(os.listdir(os.path.dirname(script_location)))
            except Exception as e:
                logger.error(f"无法列出目录内容: {e}")
            return False
            
        # 检查版本目录
        versions_dir = os.path.join(script_location, 'versions')
        logger.info(f"检查版本目录: {versions_dir}")
        if os.path.exists(versions_dir):
            logger.info("版本目录存在，内容:")
            try:
                versions = os.listdir(versions_dir)
                logger.info(str(versions))
                if not any(f.endswith('.py') for f in versions):
                    logger.warning("警告: 版本目录中没有找到 .py 文件")
            except Exception as e:
                logger.error(f"无法列出版本目录内容: {e}")
        else:
            logger.warning("警告: 版本目录不存在")
            return False
        
        alembic_cfg.set_main_option('script_location', script_location)
        
        # 使用 get_database_url() 获取正确的数据库 URL
        db_url = get_database_url()
        # 替换 URL scheme
        db_url = db_url.replace('sqlite+aiosqlite://', 'sqlite://')
        logger.info(f"数据库URL: {db_url}")
        alembic_cfg.set_main_option('sqlalchemy.url', db_url)
        
        # 检查数据库文件目录是否存在
        db_path = db_url.replace('sqlite:///', '')
        db_dir = os.path.dirname(db_path)
        logger.info(f"数据库文件路径: {db_path}")
        
        if not os.path.exists(db_dir):
            logger.info(f"创建数据库目录: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
        
        # 检查数据库文件
        if os.path.exists(db_path):
            logger.info("数据库文件已存在")
            # 检查数据库是否可写
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.close()
                logger.info("数据库连接测试成功")
            except Exception as e:
                logger.error(f"数据库连接测试失败: {e}")
                return False
        else:
            logger.info("数据库文件不存在，将在迁移时创建")
            # 尝试创建空数据库文件
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.close()
                logger.info("成功创建空数据库文件")
            except Exception as e:
                logger.error(f"创建数据库文件失败: {e}")
                return False
        
        # 运行迁移前检查 alembic_version 表
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            logger.info(f"现有数据库表: {tables}")
            conn.close()
        except Exception as e:
            logger.error(f"检查数据库表失败: {e}")
        
        # 运行迁移
        logger.info("\n开始执行数据库升级...")
        try:
            alembic.command.upgrade(alembic_cfg, "head")
            logger.info("数据库迁移成功完成！")
        except Exception as e:
            logger.error(f"执行迁移命令时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        
        # 验证迁移结果
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            logger.info(f"迁移后的数据库表: {tables}")
            conn.close()
        except Exception as e:
            logger.error(f"验证迁移结果失败: {e}")
        
        logger.info("=== 数据库迁移完成 ===\n")
        return True
    except Exception as e:
        logger.error(f"\n数据库迁移过程中出错: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        import traceback
        logger.error("详细错误信息:")
        logger.error(traceback.format_exc())
        logger.error("=== 数据库迁移失败 ===\n")
        return False

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