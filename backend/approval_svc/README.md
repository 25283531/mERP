# 审批服务模块 (Approval Service)

## 1. 模块概述

### 模块名称及其在整个项目中的作用
审批服务模块是mERP系统的核心业务支持模块，负责企业各类业务审批流程的定义、执行和管理。该模块为系统提供统一的审批流程管理功能，支持订单、物料、生产计划等多种业务场景的审批需求。

### 主要功能点和用户交互流程
- 审批流程定义与管理
- 审批任务创建与分配
- 审批状态跟踪与查询
- 审批历史记录查看
- 多级审批流程支持

用户交互流程：
1. 业务模块触发审批请求
2. 审批服务创建审批任务并分配给相关审批人
3. 审批人进行审批操作（同意/拒绝/转交）
4. 系统记录审批结果并通知相关业务模块

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
approval_svc/
├── app.py              # 应用入口文件
├── routes.py           # 路由定义
├── controllers/        # 控制器目录
│   ├── __init__.py
│   └── approval.py     # 审批相关控制器
├── models/             # 数据模型目录
│   ├── __init__.py
│   └── approval.py     # 审批相关数据模型
├── services/           # 业务逻辑目录
│   ├── __init__.py
│   └── approval.py     # 审批相关业务逻辑
└── schemas/            # 数据模式目录
    ├── __init__.py
    └── approval.py     # 审批相关数据模式
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
- GET /api/v1/approvals: 获取审批列表
- GET /api/v1/approvals/{id}: 获取单个审批详情
- POST /api/v1/approvals: 创建新审批
- PUT /api/v1/approvals/{id}: 更新审批信息
- DELETE /api/v1/approvals/{id}: 删除审批
- POST /api/v1/approvals/{id}/approve: 审批通过
- POST /api/v1/approvals/{id}/reject: 审批拒绝
- POST /api/v1/approvals/{id}/transfer: 转交审批

### 请求和响应格式示例
创建审批请求示例：
```json
{
  "title": "采购订单审批",
  "content": "采购订单#12345需要审批",
  "type": "purchase_order",
  "business_id": "12345",
  "approver_id": "user001",
  "deadline": "2023-12-31T23:59:59"
}
```

审批响应示例：
```json
{
  "id": "apv-001",
  "title": "采购订单审批",
  "content": "采购订单#12345需要审批",
  "type": "purchase_order",
  "business_id": "12345",
  "creator_id": "system",
  "approver_id": "user001",
  "status": "pending",
  "created_at": "2023-11-01T10:30:00",
  "updated_at": "2023-11-01T10:30:00",
  "deadline": "2023-12-31T23:59:59"
}
```

## 5. 数据模型

### 核心数据模型及其关系
- Approval: 审批主表
- ApprovalHistory: 审批历史记录
- ApprovalFlow: 审批流程定义
- ApprovalStep: 审批步骤定义

### 数据库表结构和字段说明
```sql
CREATE TABLE approvals (
  id VARCHAR(36) PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  content TEXT,
  type VARCHAR(50) NOT NULL,
  business_id VARCHAR(50) NOT NULL,
  creator_id VARCHAR(36) NOT NULL,
  approver_id VARCHAR(36) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deadline TIMESTAMP
);

CREATE TABLE approval_histories (
  id VARCHAR(36) PRIMARY KEY,
  approval_id VARCHAR(36) NOT NULL,
  operator_id VARCHAR(36) NOT NULL,
  action VARCHAR(20) NOT NULL,
  comment TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (approval_id) REFERENCES approvals(id)
);
```

## 6. 业务逻辑

### 核心业务流程和规则
1. 审批创建流程
   - 业务模块通过API创建审批请求
   - 系统根据业务类型确定审批流程
   - 系统分配审批任务给相应审批人

2. 审批执行流程
   - 审批人查看待审批任务
   - 审批人进行审批操作
   - 系统记录审批结果
   - 多级审批时，系统自动流转到下一级审批人

### 关键算法和处理逻辑
- 审批流程引擎：根据预定义的流程规则，动态确定审批路径和审批人
- 审批权限验证：确保只有被分配的审批人才能进行审批操作
- 审批超时处理：对超过截止日期的审批进行自动处理或提醒

## 7. 错误处理

### 异常情况的处理策略
- 数据验证错误：返回400错误，并提供详细的验证失败信息
- 资源不存在：返回404错误，说明请求的资源不存在
- 权限不足：返回403错误，说明用户无权执行该操作
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
SERVICE_PORT=8002
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