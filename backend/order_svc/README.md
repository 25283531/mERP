# order_svc

## 功能
- 出货申请管理
- 内部审批流程触发

## 安装依赖
```bash
pip install -r requirements.txt
```

## 环境变量 (`.env`)
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=warehouse_db
DB_USER=user
DB_PASSWORD=pass
SERVICE_PORT=8001
```

## 运行
```bash
uvicorn app:app --reload --port ${SERVICE_PORT}
```