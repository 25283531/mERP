# 计划管理服务 (Plan Service)

## 1. 模块概述

### 模块名称及其在整个系统架构中的位置和作用
计划管理服务是mERP系统的核心微服务之一，负责企业生产计划的创建、管理和跟踪。本服务在整个系统中承担生产计划的制定与执行监控职责，为生产排程、物料需求计划和订单管理提供基础数据支持。

### 主要提供的服务和功能点
- 生产计划的创建、查询、更新和删除
- 计划时间管理（开始时间、结束时间）
- 计划数量管理
- 计划状态跟踪与更新
- 计划与订单、物料的关联管理

## 2. 技术栈与依赖

### 使用的后端框架及其版本
- FastAPI: 用于构建高性能API服务
- Python 3.8+: 基础编程语言

### 主要依赖库及其用途
- SQLAlchemy: ORM框架，用于数据库操作
- Pydantic: 数据验证和设置管理
- dotenv: 环境变量管理
- uvicorn: ASGI服务器，用于运行FastAPI应用

## 3. 项目结构说明

### 模块目录下各文件和子目录的作用
```
plan_svc/
├── app.py              # 应用入口，FastAPI实例配置
├── routes.py           # API路由定义
├── controllers/        # 控制器，处理请求逻辑
├── models/             # 数据库模型定义
│   └── models.py       # 定义Plan等数据模型
├── services/           # 业务逻辑层
│   └── plan_service.py # 计划相关业务逻辑
├── schemas.py          # 请求和响应模型定义
├── database.py         # 数据库连接配置
├── requirements.txt    # 依赖包列表
└── .env                # 环境变量配置
```

### 代码组织方式和模块划分
本服务采用分层架构设计：
- 表示层(routes.py): 定义API接口和路由
- 控制层(controllers/): 处理请求参数验证和响应
- 服务层(services/): 实现核心业务逻辑
- 数据层(models/): 定义数据库模型和数据访问方法

## 4. 数据模型与数据库

### 定义的数据库模型及其字段说明
主要数据模型包括：
- Plan: 生产计划基本信息
  - id: 主键，整型
  - name: 计划名称，字符串
  - start_time: 计划开始时间，日期时间类型
  - end_time: 计划结束时间，日期时间类型
  - quantity: 计划数量，浮点数

### 数据库迁移工具的使用方法
本服务使用Alembic进行数据库迁移管理：
- 创建迁移: `alembic revision --autogenerate -m "描述"`
- 应用迁移: `alembic upgrade head`
- 回滚迁移: `alembic downgrade -1`

## 5. API 接口文档

### 提供的API列表
已实现的API接口：
- POST /api/v1/plans/: 创建新计划
- GET /api/v1/plans/: 获取计划列表
- GET /api/v1/plans/{plan_id}: 获取单个计划详情
- PUT /api/v1/plans/{plan_id}: 更新计划信息
- DELETE /api/v1/plans/{plan_id}: 删除计划

### 接口的权限控制和认证方式
接口认证采用JWT令牌认证机制，通过请求头中的Authorization字段传递令牌。

## 6. 配置与环境变量

### 模块所需的配置项及其说明
主要配置项包括：
- 数据库连接信息
- 服务端口配置
- 日志级别设置
- 跨域配置

### 环境变量的设置方法和示例
在.env文件中配置以下环境变量：
```
DATABASE_URL=postgresql://user:password@localhost/plan_db
SERVICE_PORT=8002
LOG_LEVEL=INFO
ALLOW_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 7. 启动与运行

### 本地开发环境的启动步骤
1. 安装依赖: `pip install -r requirements.txt`
2. 设置环境变量或创建.env文件
3. 启动服务: `uvicorn backend.plan_svc.app:app --reload`

### 生产环境的部署方式和注意事项
生产环境部署建议：
1. 使用Docker容器化部署
2. 配置反向代理(如Nginx)处理请求转发
3. 使用Gunicorn作为WSGI服务器
4. 确保敏感配置通过环境变量注入，不要硬编码

## 8. 日志与监控

### 日志记录的格式和存储位置
日志采用JSON格式，包含时间戳、日志级别、模块名称、请求ID等信息。
日志文件默认存储在`/var/log/merp/plan_svc/`目录下。

### 监控工具的集成和使用方法
服务集成了Prometheus指标导出，可通过/metrics端点获取监控指标。
建议使用Grafana配合Prometheus进行可视化监控。

## 9. 测试与覆盖率

### 编写的单元测试和集成测试的覆盖范围
测试覆盖以下方面：
- API接口测试
- 服务层业务逻辑测试
- 数据模型测试
- 边界条件和异常处理测试

### 测试运行的方法和生成测试报告的方式
运行测试：`pytest tests/`
生成覆盖率报告：`pytest --cov=backend.plan_svc tests/`

## 10. 常见问题与解决方案

### 开发过程中可能遇到的问题及其解决方法
1. 数据库连接失败
   - 检查数据库服务是否运行
   - 验证连接字符串格式是否正确
   - 确认网络连接和防火墙设置

2. API响应缓慢
   - 检查数据库查询是否优化
   - 考虑添加适当的缓存机制
   - 分析并优化复杂业务逻辑

### 模块的限制和已知问题
- 大批量计划导入时可能存在性能瓶颈
- 复杂计划依赖关系的处理逻辑有待优化
- 当前版本不支持计划的自动调整和优化