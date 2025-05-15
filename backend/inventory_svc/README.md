# 库存服务模块 (Inventory Service)

## 1. 模块概述

### 模块名称及其在整个项目中的作用
库存服务模块是mERP系统的核心业务模块，负责企业物料和产品库存的管理与追踪。该模块为系统提供实时库存数据，支持入库、出库、库存调拨、盘点等操作，是企业物料资源管理的重要组成部分。

### 主要功能点和用户交互流程
- 库存入库与出库管理
- 库存盘点与调整
- 库存调拨与转移
- 库存预警与报表
- 批次与序列号管理

用户交互流程：
1. 用户通过库存管理界面查看当前库存状态
2. 执行入库、出库、调拨等库存操作
3. 系统记录库存变动并更新库存数量
4. 生成库存报表和预警信息

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
inventory_svc/
├── app.py              # 应用入口文件
├── routes.py           # 路由定义
├── controllers/        # 控制器目录
│   ├── __init__.py
│   └── inventory.py    # 库存相关控制器
├── models/             # 数据模型目录
│   ├── __init__.py
│   └── inventory.py    # 库存相关数据模型
├── services/           # 业务逻辑目录
│   ├── __init__.py
│   └── inventory.py    # 库存相关业务逻辑
└── schemas/            # 数据模式目录
    ├── __init__.py
    └── inventory.py    # 库存相关数据模式
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
- GET /api/v1/inventories: 获取库存列表
- GET /api/v1/inventories/{id}: 获取单个库存详情
- POST /api/v1/inventories/in: 创建入库记录
- POST /api/v1/inventories/out: 创建出库记录
- POST /api/v1/inventories/transfer: 创建库存调拨记录
- POST /api/v1/inventories/adjust: 调整库存数量
- GET /api/v1/inventories/report: 获取库存报表
- GET /api/v1/inventories/alert: 获取库存预警信息

### 请求和响应格式示例
入库请求示例：
```json
{
  "material_id": "mat-001",
  "warehouse_id": "wh-001",
  "quantity": 100,
  "batch_no": "B20231101",
  "source_type": "purchase",
  "source_id": "po-001",
  "remark": "采购入库"
}
```

库存响应示例：
```json
{
  "id": "inv-001",
  "material_id": "mat-001",
  "material_name": "原材料A",
  "warehouse_id": "wh-001",
  "warehouse_name": "主仓库",
  "quantity": 100,
  "batch_no": "B20231101",
  "unit": "个",
  "created_at": "2023-11-01T10:30:00",
  "updated_at": "2023-11-01T10:30:00"
}
```

## 5. 数据模型

### 核心数据模型及其关系
- Inventory: 库存主表
- InventoryTransaction: 库存交易记录
- Warehouse: 仓库信息
- Material: 物料信息（关联物料服务）

### 数据库表结构和字段说明
```sql
CREATE TABLE inventories (
  id VARCHAR(36) PRIMARY KEY,
  material_id VARCHAR(36) NOT NULL,
  warehouse_id VARCHAR(36) NOT NULL,
  quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
  batch_no VARCHAR(50),
  unit VARCHAR(20) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY (material_id, warehouse_id, batch_no)
);

CREATE TABLE inventory_transactions (
  id VARCHAR(36) PRIMARY KEY,
  inventory_id VARCHAR(36) NOT NULL,
  transaction_type ENUM('in', 'out', 'transfer', 'adjust') NOT NULL,
  quantity DECIMAL(10,2) NOT NULL,
  source_type VARCHAR(50),
  source_id VARCHAR(36),
  operator_id VARCHAR(36) NOT NULL,
  remark TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (inventory_id) REFERENCES inventories(id)
);
```

## 6. 业务逻辑

### 核心业务流程和规则
1. 库存入库流程
   - 接收入库请求（采购、生产、退货等）
   - 验证物料和仓库信息
   - 更新库存数量
   - 记录入库交易

2. 库存出库流程
   - 接收出库请求（销售、生产领料、报废等）
   - 验证库存是否充足
   - 更新库存数量
   - 记录出库交易

### 关键算法和处理逻辑
- 库存计算：基于先进先出(FIFO)原则计算库存成本和数量
- 库存预警：根据设定的安全库存量，自动生成库存预警
- 批次管理：支持按批次管理库存，实现批次追踪

## 7. 错误处理

### 异常情况的处理策略
- 库存不足：返回400错误，说明库存不足无法出库
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
DB_NAME=merp_db
DB_USER=merp_user
DB_PASSWORD=password
SERVICE_PORT=8004
LOG_LEVEL=INFO
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