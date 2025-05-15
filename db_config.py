#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接配置文件

该文件集中管理mERP系统所有数据库连接信息，包括主机地址、端口、用户名、密码等。
修改此文件中的配置后，所有服务和脚本将自动使用新的数据库连接信息。
"""
import os
import logging

# 配置日志
logger = logging.getLogger('db_config')

# 从环境变量获取数据库连接信息
def get_env(key, default=None):
    return os.environ.get(key, default)

# 数据库连接配置
DB_HOST = get_env('DB_HOST', 'localhost')
DB_PORT = int(get_env('DB_PORT', 3306))
DB_USER = get_env('DB_USER', 'root')
DB_PASSWORD = get_env('DB_PASSWORD', '123456')  # 默认空密码
DEFAULT_DB_NAME = get_env('DB_NAME', 'merp_db')  # 默认数据库名

# 各服务特定的数据库名
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

# 打印数据库连接信息的函数（不包含密码）
def log_db_info():
    logger.info(f"数据库连接信息: 主机={DB_HOST}, 端口={DB_PORT}, 用户={DB_USER}")
    logger.info(f"默认数据库名: {DEFAULT_DB_NAME}")

# 获取特定服务的数据库名
def get_service_db_name(service_name):
    return SERVICE_DB_NAMES.get(service_name, DEFAULT_DB_NAME)