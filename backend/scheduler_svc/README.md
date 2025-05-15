# 调度服务模块 (Scheduler Service)

## 1. 模块概述

### 模块名称及其在整个项目中的作用
调度服务模块是mERP系统的基础支持模块，负责系统中各类定时任务和计划任务的调度与执行。该模块为系统提供统一的任务调度管理功能，支持生产计划、库存盘点、数据同步等多种业务场景的自动化执行。

### 主要功能点和用户交互流程
- 定时任务创建与管理
- 计划任务调度与执行
- 任务执行状态监控
- 任务执行历史记录
- 任务优先级管理

用户交互流程：
1. 管理员创建或配置调度任务
2. 系统按照预定义的时间或条件执行任务
3. 系统记录任务执行结果和状态
4. 管理员查看任务执行历史和状态报告

## 2. 技术栈与依赖

### 使用的框架及其版本
- FastAPI: 后端API框架
- SQLAlchemy: ORM框架
- Pydantic: 数据验证
- APScheduler: 任务调度框架

### 主要依赖库及其用途
- fastapi: Web框架，提供API接口
- sqlalchemy: 数据库ORM，处理数据持久化
- pydantic: 数据验证和序列化
- apscheduler: 任务调度库，管理定时任务
- uvicorn: ASGI服务器，运行FastAPI应用
- python-dotenv: 环境变量管理

## 3. 文件结构说明

### 模块目录下各文件和子目录的作用
```
scheduler_svc/
├── app.py              # 应用入口文件
├── routes.py           # 路由定义
├── controllers/        # 控制器目录
│   ├── __init__.py
│   └── scheduler.py    # 调度相关控制器
├── models/             # 数据模型目录
│   ├── __init__.py
│   └── scheduler.py    # 调度相关数据模型
├── services/           # 业务逻辑目录
│   ├── __init__.py
│   └── scheduler.py    # 调度相关业务逻辑
└── jobs/               # 任务定义目录
    ├── __init__.py
    └── tasks.py        # 预定义任务
```

### 组件划分和职责说明
- app.py: 应用程序入口，负责初始化FastAPI应用和注册路由
- routes.py: 定义API路由和端点
- controllers/: 包含处理HTTP请求的控制器
- models/: 定义数据库模型和ORM映射
- services/: 实现业务逻辑和规则
- jobs/: 包含预定义任务和任务执行逻辑

## 4. API接口列表

### 模块提供的API端点及其功能描述
- GET /api/v1/jobs: 获取任务列表
- GET /api/v1/jobs/{id}: 获取单个任务详情
- POST /api/v1/jobs: 创建新任务
- PUT /api/v1/jobs/{id}: 更新任务信息
- DELETE /api/v1/jobs/{id}: 删除任务
- POST /api/v1/jobs/{id}/execute: 立即执行任务
- POST /api/v1/jobs/{id}/pause: 暂停任务
- POST /api/v1/jobs/{id}/resume: 恢复任务
- GET /api/v1/jobs/history: 获取任务执行历史

### 请求和响应格式示例
创建任务请求示例：
```json
{
  "name": "库存盘点任务",
  "job_type": "cron",
  "func": "inventory_check",
  "cron_expression": "0 0 1 * *",
  "args": ["all"],
  "kwargs": {"detailed": true},
  "description": "每月1日凌晨执行库存盘点"
}
```

任务响应示例：
```json
{
  "id": "job-001",
  "name": "库存盘点任务",
  "job_type": "cron",
  "func": "inventory_check",
  "cron_expression": "0 0 1 * *",
  "args": ["all"],
  "kwargs": {"detailed": true},
  "status": "active",
  "next_run_time": "2023-12-01T00:00:00",
  "description": "每月1日凌晨执行库存盘点",
  "created_at": "2023-11-01T10:30:00",
  "updated_at": "2023-11-01T10:30:00",
  "created_by": "admin"
}
```

## 5. 数据模型

### 核心数据模型及其关系
- Job: 任务定义表
- JobExecution: 任务执行记录表
- JobDependency: 任务依赖关系表

### 数据库表结构和字段说明
```sql
CREATE TABLE jobs (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  job_type VARCHAR(20) NOT NULL,
  func VARCHAR(100) NOT NULL,
  cron_expression VARCHAR(100),
  interval_seconds INT,
  args TEXT,
  kwargs TEXT,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  next_run_time TIMESTAMP,
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by VARCHAR(36) NOT NULL
);

CREATE TABLE job_executions (
  id VARCHAR(36) PRIMARY KEY,
  job_id VARCHAR(36) NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  status VARCHAR(20) NOT NULL,
  result TEXT,
  error TEXT,
  FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

## 6. 业务逻辑

### 核心业务流程和规则
1. 任务调度流程
   - 系统启动时加载所有活跃任务
   - 根据任务类型和时间表达式计算下次执行时间
   - 到达执行时间时触发任务执行
   - 记录任务执行结果和状态

2. 任务管理流程
   - 管理员创建或更新任务定义
   - 系统验证任务参数和表达式
   - 更新调度器中的任务信息
   - 任务状态变更（暂停/恢复/删除）

### 关键算法和处理逻辑
- 任务调度算法：基于时间表达式计算任务执行时间
- 任务优先级处理：确保高优先级任务优先执行
- 任务依赖管理：处理任务之间的依赖关系和执行顺序

## 7. 错误处理

### 异常情况的处理策略
- 任务执行失败：记录错误信息，根据配置决定是否重试
- 任务参数错误：返回400错误，并提供详细的验证失败信息
- 资源不存在：返回404错误，说明请求的任务不存在
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
SERVICE_PORT=8005
LOG_LEVEL=INFO
JOB_STORE=sqlalchemy
```

## 9. 测试

### 单元测试和集成测试策略
- 使用pytest进行单元测试和集成测试
- 模拟调度器环境进行测试
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