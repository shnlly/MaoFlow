import asyncio
from logging.config import fileConfig
import logging
import os
import sys

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy import engine_from_config

from alembic import context
from dotenv import load_dotenv

from core.config import settings
from core.database import Base

# 设置日志
logger = logging.getLogger('alembic.migration')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 加载环境变量
load_dotenv('.env.development')

# 这里导入所有的模型
from app.system.models import User
from app.llm.models import Conversation, Message, MessageItem, LLMModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 设置 SQLAlchemy URL
config.set_main_option("sqlalchemy.url", settings.SQLITE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 获取数据库路径
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'maoflow.db'))
db_url = f"sqlite+aiosqlite:///{db_path}"
logger.info(f"数据库路径: {db_path}")
logger.info(f"数据库URL: {db_url}")

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    logger.info("运行离线迁移...")
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
    logger.info("离线迁移完成")

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    logger.info("运行在线迁移...")
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

    logger.info("在线迁移完成")

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
