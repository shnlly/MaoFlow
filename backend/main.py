import argparse
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.database import run_migrations
from app.system.routers import user_router
from app.llm.routers import conversation_router, message_router, model_router
from app.api.api_v1.api import api_router

# 解析命令行参数
parser = argparse.ArgumentParser(description='MaoFlow Backend Server')
parser.add_argument('--db-path', type=str, help='SQLite数据库文件的路径')
args = parser.parse_args()

# 如果指定了数据库路径，更新配置
if args.db_path:
    settings.DB_PATH = args.db_path
elif os.environ.get('MAOFLOW_DB_PATH'):
    settings.DB_PATH = os.environ.get('MAOFLOW_DB_PATH')

# 确保数据库目录存在
if settings.DB_PATH:
    db_dir = Path(settings.DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json" if settings.docs_enabled else None,
    docs_url=f"{settings.API_PREFIX}/docs" if settings.docs_enabled else None,
    redoc_url=f"{settings.API_PREFIX}/redoc" if settings.docs_enabled else None,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS
)

# 注册路由
app.include_router(user_router, prefix=settings.API_PREFIX)
app.include_router(conversation_router, prefix=settings.API_PREFIX)
app.include_router(message_router, prefix=settings.API_PREFIX)
app.include_router(model_router, prefix=settings.API_PREFIX)
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    # 运行数据库迁移
    run_migrations()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
