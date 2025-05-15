# 班次服务模块 (Shift Service)

## 1. 模块概述

### 模块名称及其在整个项目中的作用
班次服务模块是mERP系统的生产管理支持模块，负责企业生产班次和排班的管理与规划。该模块为系统提供班次定义、排班计划和考勤管理功能，是生产计划执行和人力资源管理的重要支撑。

### 主要功能点和用户交互流程
- 班次类型定义与管理
- 生产排班计划制定
- 员工排班管理
- 考勤记录与统计
- 班次调整与变更

用户交互流程：
1. 管理员定义班次类型和工作时间
2. 生产主管制定排班计划
3. 员工查看个人排班信息
4. 系统记录考勤数据并生成统计报表

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
shift_svc/
├── app.py              # 应用入口文件
├── routes.py           # 路由定义
├── controllers/        # 控制器目录
│   ├── __init__.py
│   └── shift.py        # 班次相关控制器
├── models/             # 数据模型目录
│   ├── __init__.py
│   └── shift.py        # 班次相关数据模型
├── services/           # 业务逻辑目录
│   ├── __init__.py
│   └── shift.py        # 班次相关业务逻辑
└── schemas/            # 数据模式目录
    ├── __init__.py
    └── shift.py        # 班次相关数据模式
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
- GET /api/v1/shifts: 获取班次列表
- GET /api/v1/shifts/{id}: 获取单个班次详情
- POST /api/v1/shifts: 创建新班次
- PUT /api/v1/shifts/{id}: 更新班次信息
- DELETE /api/v1/shifts/{id}: 删除班次
- GET /api/v1/schedules: 获取排班计划列表
- POST /api/v1/schedules: 创建排班计划
- PUT /api/v1/schedules/{id}: 更新排班计划
- GET /api/v1/attendances: 获取考勤记录
- POST /api/v1/attendances: 创建考勤记录

### 请求和响应格式示例
创建班次请求示例：
```json
{
  "name": "早班",
  "start_time": "08:00:00",
  "end_time": "16:00:00",
  "break_time": 60,
  "is_night_shift": false,
  "description": "标准日班"
}
```

班次响应示例：
```json
{
  "id": "shift-001",
  "name": "早班",
  "start_time": "08:00:00",
  "end_time": "16:00:00",
  "break_time": 60,
  "is_night_shift": false,
  "work_hours": 7,
  "description": "标准日班",
  "created_at": "2023-11-01T10:30:00",
  "updated_at": "2023-11-01T10:30:00"
}
```

## 5. 数据模型

### 核心数据模型及其关系
- Shift: 班次定义表
- Schedule: 排班计划表
- Attendance: 考勤记录表
- Employee: 员工信息（关联人力资源服务）

### 数据库表结构和字段说明
```sql
CREATE TABLE shifts (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  break_time INT NOT NULL DEFAULT 0,
  is_night_shift BOOLEAN NOT NULL DEFAULT false,
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE schedules (
  id VARCHAR(36) PRIMARY KEY,
  employee_id VARCHAR(36) NOT NULL,
  shift_id VARCHAR(36) NOT NULL,
  work_date DATE NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'planned',
  remark TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by VARCHAR(36) NOT NULL,
  UNIQUE KEY (employee_id, work_date),
  FOREIGN KEY (shift_id) REFERENCES shifts(id)
);
```

## 6. 业务逻辑

### 核心业务流程和规则
1. 班次定义流程
   - 管理员创建班次类型
   - 设置班次工作时间和休息时间
   - 系统计算有效工作时长

2. 排班计划流程
   - 生产主管创建排班计划
   - 系统验证排班合理性（如连续工作时间）
   - 通知相关员工排班信息
   - 记录排班变更历史

### 关键算法和处理逻辑
- 工时计算：计算不同班次的有效工作时长
- 排班优化：根据员工技能和工作负载平衡排班
- 考勤统计：汇总员工出勤情况和工作时长

## 7. 错误处理

### 异常情况的处理策略
- 排班冲突：返回400错误，说明员工在同一时间已有其他排班
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
SERVICE_PORT=8006
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