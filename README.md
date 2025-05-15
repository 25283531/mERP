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

## 数据库配置
项目使用集中式数据库配置文件 `db_config.py`，位于项目根目录。修改此文件可以更改所有服务和脚本使用的数据库连接信息：

```python
# 数据库连接配置
DB_HOST = get_env('DB_HOST', 'localhost')  # 数据库主机地址
DB_PORT = int(get_env('DB_PORT', 3306))    # 数据库端口
DB_USER = get_env('DB_USER', 'root')       # 数据库用户名
DB_PASSWORD = get_env('DB_PASSWORD', '')   # 数据库密码
DEFAULT_DB_NAME = get_env('DB_NAME', 'merp_db')  # 默认数据库名
```

您也可以通过环境变量设置这些值，环境变量优先级高于配置文件中的默认值。

## 快速启动
1. 安装 MySQL 并创建数据库  
2. 根据需要修改项目根目录的 `db_config.py` 文件中的数据库连接信息  
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