#!/usr/bin/env python3
import uvicorn
from main import create_app
import os
import sys

if __name__ == "__main__":
    # 从配置获取默认值（需确保已正确加载环境变量）
    from core.config import get_settings
    settings = get_settings()
    
    # 创建应用实例
    app = create_app()
    
    # 获取工作目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境
        work_dir = os.path.dirname(sys.executable)
    else:
        work_dir = os.getcwd()
    
    print(f"Working directory: {work_dir}")
    print(f"Starting server at http://{settings.HOST}:{settings.PORT}")
    
    # 启动服务器
    uvicorn.run(
        app=app,
        host="0.0.0.0",  # 允许外部访问
        port=settings.PORT,
        ssl_certfile=None,  # 明确禁用SSL
        ssl_keyfile=None,
        reload=False,
        log_config=None,
        access_log=True  # 启用访问日志以便调试
    )