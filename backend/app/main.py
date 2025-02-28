from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import config_router, conversation_router, chat_router

app = FastAPI(title="MaoFlow API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(config_router)
app.include_router(conversation_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "Welcome to MaoFlow API"} 