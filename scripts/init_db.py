#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化 MySQL 数据库结构脚本

该脚本用于创建mERP系统所需的所有数据库，并进行基本初始化。
脚本会根据main.py中定义的SERVICE_DB_NAMES创建对应的数据库。
"""
import os
import sys
import pymysql
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('db_initializer')

# 添加项目根目录到PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

# 导入数据库配置
try:
    from db_config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DEFAULT_DB_NAME, SERVICE_DB_NAMES, log_db_info
    logger.info(f"成功导入数据库配置")
    log_db_info()
except ImportError:
    logger.warning("无法导入db_config.py，将使用默认配置")
    # 尝试从main.py导入
    try:
        from backend.main import SERVICE_DB_NAMES
        logger.info(f"成功从main.py导入服务数据库配置")
    except ImportError:
        logger.warning("无法导入main.py中的SERVICE_DB_NAMES，将使用默认配置")
        # 默认的服务数据库名称配置
        SERVICE_DB_NAMES = {
            'plan_svc': 'merp_plan_svc',
            'order_svc': 'merp_order_svc',
            'inventory_svc': 'merp_inventory_svc',
            'material_svc': 'merp_material_svc',
            'config_svc': 'merp_config_svc',
            'approval_svc': 'merp_approval_svc',
            'scheduler_svc': 'merp_scheduler_svc',
            'shift_svc': 'merp_shift_svc'
        }
    
    # 从环境变量获取数据库连接信息
    def get_env(key, default=None):
        return os.environ.get(key, default)
    
    # 数据库连接配置
    DB_HOST = get_env('DB_HOST', 'localhost')
    DB_PORT = int(get_env('DB_PORT', 3306))
    DB_USER = get_env('DB_USER', 'root')
    DB_PASSWORD = get_env('DB_PASSWORD', '')  # 默认空密码
    DEFAULT_DB_NAME = get_env('DB_NAME', 'merp_db')  # 默认数据库名
    
    # 打印数据库连接信息（不包含密码）
    logger.info(f"数据库连接信息: 主机={DB_HOST}, 端口={DB_PORT}, 用户={DB_USER}")
    logger.info(f"默认数据库名: {DEFAULT_DB_NAME}")

# 检查是否需要交互式输入密码
if not DB_PASSWORD:
    import getpass
    logger.info("未设置数据库密码，请输入MySQL密码（如无密码请直接回车）:")
    DB_PASSWORD = getpass.getpass("MySQL密码: ")

# 基本表结构定义
BASIC_TABLES = {
    # 配置服务基本表结构
    'merp_config_svc': [
        """
        CREATE TABLE IF NOT EXISTS system_config (
            id INT AUTO_INCREMENT PRIMARY KEY,
            config_key VARCHAR(100) NOT NULL,
            config_value TEXT,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY (config_key)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ],
    
    # 审批服务基本表结构
    'merp_approval_svc': [
        """
        CREATE TABLE IF NOT EXISTS approval_workflow (
            id INT AUTO_INCREMENT PRIMARY KEY,
            workflow_name VARCHAR(100) NOT NULL,
            description TEXT,
            status ENUM('active', 'inactive') DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS approval_step (
            id INT AUTO_INCREMENT PRIMARY KEY,
            workflow_id INT NOT NULL,
            step_name VARCHAR(100) NOT NULL,
            step_order INT NOT NULL,
            approver_role VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (workflow_id) REFERENCES approval_workflow(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ],
    
    # 调度服务基本表结构
    'merp_scheduler_svc': [
        """
        CREATE TABLE IF NOT EXISTS scheduled_job (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id VARCHAR(100) NOT NULL,
            job_name VARCHAR(100) NOT NULL,
            job_function VARCHAR(100) NOT NULL,
            cron_expression VARCHAR(100),
            interval_seconds INT,
            job_args TEXT,
            job_kwargs TEXT,
            next_run_time TIMESTAMP NULL,
            status ENUM('active', 'paused', 'completed', 'error') DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY (job_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ],
    
    # 其他服务的基本表结构可以根据需要添加
}


def create_database(db_name):
    """
    创建数据库
    
    Args:
        db_name: 数据库名称
        
    Returns:
        bool: 是否成功创建数据库
    """
    try:
        # 连接MySQL服务器
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARSET utf8mb4;")
        conn.commit()
        
        logger.info(f"数据库 {db_name} 创建成功")
        
        cursor.close()
        conn.close()
        return True
    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        if error_code == 1045:  # 访问被拒绝
            logger.error(f"数据库访问被拒绝: 用户名或密码错误 (用户: {DB_USER}@{DB_HOST})")
            logger.info("请检查环境变量 DB_USER 和 DB_PASSWORD 是否正确设置")
        elif error_code == 2003:  # 无法连接到MySQL服务器
            logger.error(f"无法连接到MySQL服务器: {DB_HOST}:{DB_PORT}")
            logger.info("请确保MySQL服务已启动且可以访问")
        else:
            logger.error(f"数据库操作错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"创建数据库 {db_name} 失败: {str(e)}")
        return False


def initialize_database(db_name):
    """
    初始化数据库表结构
    
    Args:
        db_name: 数据库名称
    """
    if db_name not in BASIC_TABLES:
        logger.info(f"数据库 {db_name} 没有预定义的表结构，跳过初始化")
        return
    
    try:
        # 连接到指定数据库
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=db_name
        )
        cursor = conn.cursor()
        
        # 创建表
        for table_sql in BASIC_TABLES[db_name]:
            cursor.execute(table_sql)
            logger.info(f"在数据库 {db_name} 中执行SQL: {table_sql[:60]}...")
        
        conn.commit()
        logger.info(f"数据库 {db_name} 表结构初始化完成")
        
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"初始化数据库 {db_name} 表结构失败: {str(e)}")


def main():
    """
    主函数，创建并初始化所有数据库
    """
    logger.info("开始初始化数据库...")
    
    # 首先创建默认数据库
    if create_database(DEFAULT_DB_NAME):
        initialize_database(DEFAULT_DB_NAME)
    
    # 然后创建各个服务的数据库
    for service_name, db_name in SERVICE_DB_NAMES.items():
        logger.info(f"正在为服务 {service_name} 创建数据库 {db_name}...")
        if create_database(db_name):
            initialize_database(db_name)
    
    logger.info("数据库初始化完成")


if __name__ == '__main__':
    main()