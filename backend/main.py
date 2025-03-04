from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn.lifespan.on  # 显式导入生命周期组件

from core.config import get_settings
from app.system.routers import user_router
from app.llm.routers import conversation_router, message_router, model_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在开发环境中允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 注册路由
app.include_router(user_router, prefix=settings.API_PREFIX)
app.include_router(conversation_router, prefix=settings.API_PREFIX)
app.include_router(message_router, prefix=settings.API_PREFIX)
app.include_router(model_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }

def create_app():
    """ASGI工厂函数"""
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
