from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from app.system.routers import user_router
from app.llm.routers import conversation_router, message_router,model_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
    allow_credentials=True
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