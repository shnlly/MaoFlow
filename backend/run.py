#!/usr/bin/env python3
import uvicorn
from main import create_app
import os
import sys
from core.database import run_migrations, get_database_url

if __name__ == "__main__":
    print("\n=== 应用启动 ===")
    # 从配置获取默认值（需确保已正确加载环境变量）
    from core.config import get_settings
    settings = get_settings()
    
    # 获取工作目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境
        work_dir = os.path.dirname(sys.executable)
        print("运行环境: 打包环境")
    else:
        work_dir = os.getcwd()
        print("运行环境: 开发环境")
    
    print(f"工作目录: {work_dir}")
    
    # 检查数据库文件路径
    db_url = get_database_url()
    db_path = db_url.replace('sqlite+aiosqlite:///', '')
    db_dir = os.path.dirname(db_path)
    
    print("\n=== 数据库配置 ===")
    print(f"数据库文件路径: {db_path}")
    print(f"数据库目录: {db_dir}")
    
    # 确保数据库目录存在
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"创建数据库目录: {db_dir}")
        except Exception as e:
            print(f"创建数据库目录失败: {e}")
            print(f"错误类型: {type(e).__name__}")
            sys.exit(1)
    else:
        print("数据库目录已存在")
    
    # 检查目录权限
    try:
        test_file = os.path.join(db_dir, '.test_write')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("数据库目录权限检查通过")
    except Exception as e:
        print(f"数据库目录权限检查失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        sys.exit(1)
    
    # 检查数据库文件
    if os.path.exists(db_path):
        print(f"数据库文件已存在: {db_path}")
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("现有数据库表:")
            for table in tables:
                print(f"  - {table[0]}")
            conn.close()
        except Exception as e:
            print(f"检查数据库表失败: {e}")
    else:
        print("数据库文件不存在，将在迁移时创建")
    
    print("\n=== 运行数据库迁移 ===")
    if not run_migrations():
        print("数据库迁移失败")
        sys.exit(1)
    
    # 创建应用实例
    print("\n=== 创建应用实例 ===")
    app = create_app()
    
    print(f"\n启动服务器: http://{settings.HOST}:{settings.PORT}")
    
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