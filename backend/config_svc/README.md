# config_svc

本服务为配置管理服务，负责系统配置项的统一管理与分发。

## 目录结构
- app.py：服务启动入口
- routes.py：路由定义
- controllers/：控制器目录
- services/：业务逻辑目录
- models/：数据模型目录
- .env.example：环境变量示例

## 启动方式
```bash
uvicorn app:app --reload
```

## 环境变量
请参考 .env.example 文件进行配置。