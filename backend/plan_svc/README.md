# 生产计划服务 (plan_svc)

本服务负责管理生产计划相关的功能，包括创建、读取、更新和删除生产计划。

## 运行服务

1.  **安装依赖**: 在 `plan_svc` 目录下, 运行 `pip install -r requirements.txt` 来安装所有必要的Python包。
2.  **配置环境变量**: 复制 `.env.example` 文件为 `.env`，并根据你的数据库设置填写正确的数据库连接信息 (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)。
3.  **启动服务**: 在 `plan_svc` 目录下, 使用Uvicorn运行服务：
    ```bash
    uvicorn app:app --reload --port 5001
    ```
    服务将在 `http://localhost:5001` 上可用。

## 环境变量

服务需要以下环境变量来进行数据库连接配置 (在 `.env` 文件中设置):

-   `DB_USER`: 数据库用户名
-   `DB_PASSWORD`: 数据库密码
-   `DB_HOST`: 数据库主机名 (例如 `localhost`)
-   `DB_PORT`: 数据库端口 (例如 `3306` for MySQL)
-   `DB_NAME`: 数据库名称 (例如 `merp_plan_svc`)

## API 接口

服务提供以下API端点:

-   `GET /api/v1/plans/`: 获取所有生产计划。
    -   可选查询参数: `skip` (int, 默认为0), `limit` (int, 默认为100)。
-   `POST /api/v1/plans/`: 创建新的生产计划。
    -   请求体: `PlanCreate` schema (包含 `name`, `start_time`, `end_time`, `quantity`)。
-   `GET /api/v1/plans/{plan_id}`: 根据ID获取指定的生产计划。
-   `PUT /api/v1/plans/{plan_id}`: 更新指定的生产计划。
    -   请求体: `PlanUpdate` schema (所有字段可选)。
-   `DELETE /api/v1/plans/{plan_id}`: 删除指定的生产计划。

服务启动后，您可以通过访问 `http://localhost:5001/docs` 查看交互式API文档 (Swagger UI)。