# MaoFlow Backend

MaoFlow 是一个基于 FastAPI 和 SQLAlchemy 构建的现代化对话系统后端。

## 项目结构

```
app_new/
├── core/           # 核心功能模块
├── system/         # 系统管理模块
├── llm/           # 大语言模型对话模块
├── shared/        # 共享工具和常量
└── alembic/       # 数据库迁移
```

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
复制 `.env.development` 文件并根据需要修改配置：
```bash
cp .env.development .env
```

3. 初始化数据库：
```bash
alembic upgrade head
```

4. 运行服务：
```bash
uvicorn main:app --reload
```

## API 文档

启动服务后，访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

### 添加新的模型

1. 在相应的应用目录下的 `models` 目录中创建模型
2. 在 `alembic/env.py` 中导入新模型
3. 创建新的迁移：
```bash
alembic revision --autogenerate -m "Add new model"
```
4. 应用迁移：
```bash
alembic upgrade head
```

### 添加新的路由

1. 在相应的应用目录下创建：
   - schemas/
   - services/
   - routers/
2. 在应用的 `__init__.py` 中导出新组件
3. 在 `main.py` 中注册新路由

## 测试

运行测试：
```bash
pytest
```

## 部署

1. 构建 Docker 镜像：
```bash
docker build -t maoflow-backend .
```

2. 运行容器：
```bash
docker run -d -p 8000:8000 maoflow-backend
``` 