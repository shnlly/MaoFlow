# MaoFlow

一个基于 Electron + FastAPI + React 的跨平台应用。

## 项目结构

```
MaoFlow/
├── backend/               # Python FastAPI 后端
│   ├── app/              # 后端应用代码
│   │   └── main.py       # 主入口文件
│   ├── config/           # 配置文件
│   ├── tests/            # 测试文件
│   ├── .env.development  # 开发环境配置
│   └── requirements.txt  # Python 依赖
├── web-ui/               # 前端代码（React）
│   ├── src/
│   │   ├── api/         # API 客户端
│   │   ├── assets/      # 静态资源
│   │   ├── components/  # UI 组件
│   │   ├── pages/       # 页面组件
│   │   ├── types/       # TypeScript 类型定义
│   │   └── utils/       # 工具函数
│   ├── public/          # 公共资源
│   ├── .env.development # 开发环境配置
│   └── package.json     # 前端依赖
├── electron/             # Electron 相关代码
│   ├── main/            # 主进程代码
│   └── preload/         # 预加载脚本
├── package.json         # 项目依赖
└── README.md           # 项目说明
```

## 环境要求

- Node.js 18+
- Python 3.8+

## 开发环境设置

1. 安装后端依赖

```bash
cd backend
python -m venv venv  # 创建虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. 安装前端依赖

```bash
# 安装根目录依赖
npm install

# 安装前端依赖
cd web-ui
npm install
```

## 启动项目

### 开发模式

1. 启动后端服务

```bash
npm dev:api
```

2. 启动前端开发服务器

```bash
# Web 开发模式
npm dev:web

# Electron 开发模式
npm dev
```

### 生产模式

1. 构建前端

```bash
npm build:web
```

2. 打包 Electron 应用

```bash
npm build:electron
```

打包后的应用将在 `out` 目录中生成。

## API 文档

启动后端服务后，可以访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 许可证

[MIT License](LICENSE)
