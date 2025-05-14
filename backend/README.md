# 后端服务总览

本目录包含七个独立的 Python 微服务，每个服务均为 FastAPI 应用，负责不同业务模块。

## 服务列表
- order_svc：出货申请与审批
- approval_svc：审批流管理
- scheduler_svc：排班与调度
- material_svc：物料管理
- inventory_svc：库存管理
- shift_svc：班次管理
- config_svc：配置与参数

每个服务目录下均有独立的 README、app.py、controllers、services、models、routes.py 等结构。

## 依赖安装
各服务目录下执行：
```bash
pip install -r requirements.txt
```

## 运行
以 order_svc 为例：
```bash
uvicorn app:app --reload --port 8001
```