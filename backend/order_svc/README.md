# 订单服务模块 (Order Service)

## 1. 模块概述

### 模块名称及其在整个项目中的作用
订单服务模块是mERP系统的核心业务模块，负责企业订单的全生命周期管理。该模块处理销售订单、采购订单等各类订单的创建、审批、执行和跟踪，是连接企业销售、采购、生产和库存等环节的重要纽带。

### 主要功能点和用户交互流程
- 出货申请管理
- 内部审批流程触发
- 销售订单管理
- 采购订单管理
- 订单状态跟踪
- 订单报表与分析

用户交互流程：
1. 用户创建新订单或查询现有订单
2. 系统触发订单审批流程
3. 审批通过后，订单进入执行阶段
4. 系统跟踪订单执行状态并更新相关信息

## 2. 技术栈与依赖

### 使用的框架及其版本
- FastAPI: 后端API框架
- SQLAlchemy: ORM框架
- Pydantic: 数据验证

### 主要依赖库及其用途
- fastapi: Web框架，提供API接口
- sqlalchemy: 数据库ORM，处理数据持久化
- pydantic: 数据验证和序列化
- uvicorn: ASGI服务器，运行FastAPI应用
- python-dotenv: 环境变量管理

## 3. 文件结构说明

### 模块目录下各文件和子目录的作用
```
order_svc/
├── app.py              # 应用入口文件
├── routes.py           # 路由定义
├── controllers/        # 控制器目录
│   ├── __init__.py
│   └── order.py        # 订单相关控制器
├── models/             # 数据模型目录
│   ├── __init__.py
│   └── order.py        # 订单相关数据模型
├── services/           # 业务逻辑目录
│   ├── __init__.py
│   └── order.py        # 订单相关业务逻辑
└── schemas/            # 数据模式目录
    ├── __init__.py
    └── order.py        # 订单相关数据模式
```

### 组件划分和职责说明
- app.py: 应用程序入口，负责初始化FastAPI应用和注册路由
- routes.py: 定义API路由和端点
- controllers/: 包含处理HTTP请求的控制器
- models/: 定义数据库模型和ORM映射
- services/: 实现业务逻辑和规则
- schemas/: 定义请求和响应的数据结构

## 4. API接口列表

### 模块提供的API端点及其功能描述
- GET /api/v1/orders: 获取订单列表
- GET /api/v1/orders/{id}: 获取单个订单详情
- POST /api/v1/orders: 创建新订单
- PUT /api/v1/orders/{id}: 更新订单信息
- DELETE /api/v1/orders/{id}: 删除订单
- POST /api/v1/orders/{id}/approve: 审批订单
- POST /api/v1/orders/{id}/reject: 拒绝订单
- GET /api/v1/orders/report: 获取订单报表

### 请求和响应格式示例
创建订单请求示例：
```json
{
  "order_type": "sales",
  "customer_id": "cust-001",
  "items": [
    {
      "product_id": "prod-001",
      "quantity": 10,
      "unit_price": 100.00
    },
    {
      "product_id": "prod-002",
      "quantity": 5,
      "unit_price": 200.00
    }
  ],
  "delivery_date": "2023-12-15",
  "remark": "紧急订单"
}
```

订单响应示例：
```json
{
  "id": "ord-001",
  "order_type": "sales",
  "customer_id": "cust-001",
  "customer_name": "ABC公司",
  "items": [
    {
      "product_id": "prod-001",
      "product_name": "产品A",
      "quantity": 10,
      "unit_price": 100.00,
      "total_price": 1000.00
    },
    {
      "product_id": "prod-002",
      "product_name": "产品B",
      "quantity": 5,
      "unit_price": 200.00,
      "total_price": 1000.00
    }
  ],
  "total_amount": 2000.00,
  "status": "pending",
  "delivery_date": "2023-12-15",
  "created_at": "2023-11-01T10:30:00",
  "updated_at": "2023-11-01T10:30:00",
  "created_by": "user001",
  "remark": "紧急订单"
}
```

## 5. 数据模型

### 核心数据模型及其关系
- Order: 订单主表
- OrderItem: 订单项目
- OrderHistory: 订单历史记录
- Customer: 客户信息（关联客户服务）
- Product: 产品信息（关联产品服务）

### 数据库表结构和字段说明
```sql
CREATE TABLE orders (
  id VARCHAR(36) PRIMARY KEY,
  order_type VARCHAR(20) NOT NULL,
  customer_id VARCHAR(36) NOT NULL,
  total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  delivery_date DATE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by VARCHAR(36) NOT NULL,
  remark TEXT
);

CREATE TABLE order_items (
  id VARCHAR(36) PRIMARY KEY,
  order_id VARCHAR(36) NOT NULL,
  product_id VARCHAR(36) NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  total_price DECIMAL(12,2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

## 6. 业务逻辑

### 核心业务流程和规则
1. 订单创建流程
   - 用户提交订单信息
   - 系统验证订单数据
   - 系统计算订单总金额
   - 创建订单记录并触发审批流程

2. 订单审批流程
   - 系统根据订单类型和金额确定审批流程
   - 通知相关审批人进行审批
   - 记录审批结果并更新订单状态

### 关键算法和处理逻辑
- 订单定价：根据客户等级、订单数量等因素计算最终价格
- 库存检查：验证产品库存是否满足订单需求
- 订单优先级：根据客户重要性和订单紧急程度确定处理优先级

## 7. 错误处理

### 异常情况的处理策略
- 库存不足：返回400错误，说明库存不足无法创建订单
- 数据验证错误：返回400错误，并提供详细的验证失败信息
- 资源不存在：返回404错误，说明请求的资源不存在
- 服务器内部错误：返回500错误，记录详细错误日志

### 日志记录和监控方案
- 使用Python标准logging模块记录应用日志
- 关键操作和错误记录到专门的日志文件
- 集成Prometheus监控系统，收集性能指标
- 设置Grafana仪表盘，可视化监控数据

## 8. 安装与配置

### 环境要求和依赖安装
- Python 3.8+
- MySQL 5.7+
- 安装依赖：`pip install -r requirements.txt`

### 配置项说明和示例
环境变量配置（.env文件）：
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=warehouse_db
DB_USER=user
DB_PASSWORD=pass
SERVICE_PORT=8001
```

## 9. 测试

### 单元测试和集成测试策略
- 使用pytest进行单元测试和集成测试
- 模拟数据库环境进行测试
- 测试覆盖核心业务逻辑和边界条件

### 测试用例和覆盖率目标
- 单元测试覆盖率目标：80%+
- 集成测试覆盖所有API端点
- 性能测试确保在高负载下系统稳定

## 10. 部署与运维

### 部署方式和环境配置
- Docker容器化部署
- Kubernetes编排管理
- CI/CD流水线自动化部署

### 监控和维护建议
- 定期检查日志文件，关注错误和警告
- 监控系统资源使用情况，及时扩容
- 定期备份数据库，确保数据安全
- 设置告警机制，对异常情况及时响应

## 运行
```bash
uvicorn app:app --reload --port ${SERVICE_PORT}
```