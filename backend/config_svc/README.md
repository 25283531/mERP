# 配置服务模块 (Config Service)

## 1. 模块概述

### 模块名称及其在整个项目中的作用
配置服务模块是mERP系统的基础支持模块，负责系统配置项的统一管理与分发。该模块为整个系统提供集中式的配置管理功能，支持动态配置更新和多环境配置管理，是系统稳定运行的重要保障。

### 主要功能点和用户交互流程
- 系统配置项的创建、编辑与删除
- 配置项分类管理
- 配置项版本控制
- 配置项访问权限控制
- 配置变更历史记录

用户交互流程：
1. 管理员通过配置管理界面查看现有配置
2. 创建新配置或修改现有配置
3. 系统记录配置变更并通知相关服务
4. 其他服务通过API获取最新配置

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
config_svc/
├── app.py              # 应用入口文件
├── routes.py           # 路由定义
├── controllers/        # 控制器目录
│   ├── __init__.py
│   └── config.py       # 配置相关控制器
├── models/             # 数据模型目录
│   ├── __init__.py
│   └── config.py       # 配置相关数据模型
├── services/           # 业务逻辑目录
│   ├── __init__.py
│   └── config.py       # 配置相关业务逻辑
└── .env.example        # 环境变量示例文件
```

### 组件划分和职责说明
- app.py: 应用程序入口，负责初始化FastAPI应用和注册路由
- routes.py: 定义API路由和端点
- controllers/: 包含处理HTTP请求的控制器
- models/: 定义数据库模型和ORM映射
- services/: 实现业务逻辑和规则

## 4. API接口列表

### 模块提供的API端点及其功能描述
- GET /api/v1/configs: 获取配置列表
- GET /api/v1/configs/{key}: 获取单个配置详情
- POST /api/v1/configs: 创建新配置
- PUT /api/v1/configs/{key}: 更新配置信息
- DELETE /api/v1/configs/{key}: 删除配置
- GET /api/v1/configs/category/{category}: 获取特定分类的配置
- GET /api/v1/configs/history/{key}: 获取配置历史记录

### 请求和响应格式示例
创建配置请求示例：
```json
{
  "key": "system.maintenance",
  "value": "false",
  "type": "boolean",
  "category": "system",
  "description": "系统维护模式开关"
}
```

配置响应示例：
```json
{
  "key": "system.maintenance",
  "value": "false",
  "type": "boolean",
  "category": "system",
  "description": "系统维护模式开关",
  "created_at": "2023-11-01T10:30:00",
  "updated_at": "2023-11-01T10:30:00",
  "created_by": "admin"
}
```

## 5. 数据模型

### 核心数据模型及其关系
- Config: 配置主表
- ConfigHistory: 配置历史记录
- ConfigCategory: 配置分类

### 数据库表结构和字段说明
```sql
CREATE TABLE configs (
  key VARCHAR(100) PRIMARY KEY,
  value TEXT NOT NULL,
  type VARCHAR(20) NOT NULL,
  category VARCHAR(50) NOT NULL,
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by VARCHAR(36) NOT NULL
);

CREATE TABLE config_histories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  config_key VARCHAR(100) NOT NULL,
  old_value TEXT,
  new_value TEXT NOT NULL,
  changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  changed_by VARCHAR(36) NOT NULL,
  FOREIGN KEY (config_key) REFERENCES configs(key)
);
```

## 6. 业务逻辑

### 核心业务流程和规则
1. 配置管理流程
   - 管理员创建或更新配置
   - 系统验证配置格式和权限
   - 系统记录配置变更历史
   - 系统通知相关服务配置已更新

2. 配置获取流程
   - 服务通过API请求配置
   - 系统验证请求权限
   - 系统返回最新配置值
   - 支持批量获取和条件过滤

### 关键算法和处理逻辑
- 配置缓存机制：减少数据库访问，提高配置获取性能
- 配置变更通知：使用事件机制通知依赖服务配置已更新
- 配置值类型转换：根据配置类型自动转换值的格式

## 7. 错误处理

### 异常情况的处理策略
- 数据验证错误：返回400错误，并提供详细的验证失败信息
- 资源不存在：返回404错误，说明请求的配置不存在
- 权限不足：返回403错误，说明用户无权操作该配置
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
SERVICE_PORT=8003
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