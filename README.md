# Warehouse Management B/S System

## 简介
基于前后端分离的 B/S 架构，前端 SPA，后端 Python 服务，统一 MySQL 存储。

## 技术栈
- 前端：Vue.js / React + TypeScript
- 后端：Python (Flask 或 FastAPI)
- 数据库：MySQL

## 目录
- `frontend/`：前端代码
- `backend/`：七大 Python 微服务
- `docs/`：架构与 API 文档
- `scripts/`：辅助脚本

## 快速启动
1. 安装 MySQL 并创建数据库  
2. 在 `backend/` 和 `frontend/` 各自复制并填写 `.env`  
3. 启动后端服务：  
   ```bash
   cd backend/order_svc
   pip install -r requirements.txt
   uvicorn app:app --reload --port 8001
   ```

4. 启动前端：

   ```bash
   cd frontend
   npm install
   npm run dev
   ```