from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.chat import router as chat_router
from .config.settings import get_settings

# 获取配置
settings = get_settings()

app = FastAPI(title="MaoFlow API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由
app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "MaoFlow API is running"}

@app.get("/api/status")
async def get_status():
    return {"status": "ok", "version": "1.0.0"} 