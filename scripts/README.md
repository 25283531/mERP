# 辅助脚本

本目录用于存放数据库初始化等辅助脚本。

## 数据库初始化脚本

- `init_db.py`：初始化 mERP 系统所需的所有 MySQL 数据库结构。

### 使用方法

1. 确保已安装必要的 Python 库：
   ```
   pip install pymysql cryptography
   ```
   > 注意：cryptography 库是 MySQL 8.0+ 密码认证所必需的

2. 数据库连接配置：
   - 方法一：修改项目根目录下的 `db_config.py` 文件（推荐）
   - 方法二：设置环境变量（优先级高于配置文件）：
   ```
   set DB_HOST=localhost
   set DB_PORT=3306
   set DB_USER=root
   set DB_PASSWORD=你的密码
   ```
   > 如果不设置密码，脚本会在运行时交互式地询问密码

3. 运行脚本：
   ```
   python init_db.py
   ```

### 常见问题解决

1. **认证错误**：如果遇到 "Access denied for user" 错误，请检查：
   - 用户名和密码是否正确
   - MySQL 用户是否有创建数据库的权限

2. **连接错误**：如果遇到 "Can't connect to MySQL server" 错误：
   - 确保 MySQL 服务已启动
   - 检查主机名和端口是否正确
   - 确认防火墙设置允许连接

### 功能说明

- 自动创建 main.py 中定义的所有微服务数据库
- 为关键服务（配置服务、审批服务、调度服务等）创建基础表结构
- 使用日志记录执行过程，便于排查问题
- 支持从环境变量读取数据库连接信息