# MaoFlow

一个基于 Electron + FastAPI + React 的跨平台应用。

## 项目结构
```
src/
├── backend/               # Python FastAPI 后端
├── ui/               # 各种前端代码
├──── web-ui/               # web代码
├──── mac-ui/               # 客户端代码
├──── win-ui/               # win前端专属代码
├──── shared-ui/               # 前端代码
├── electron/             # 打包客户端主进程专有代码
│   ├── main/            # 主进程代码
│   └── preload/         # 预加载脚本
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

