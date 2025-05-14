"""
初始化 MySQL 数据库结构脚本
"""
import os
import pymysql

def get_env(key, default=None):
    return os.environ.get(key, default)

DB_HOST = get_env('DB_HOST', 'localhost')
DB_PORT = int(get_env('DB_PORT', 3306))
DB_NAME = get_env('DB_NAME', 'warehouse_db')
DB_USER = get_env('DB_USER', 'user')
DB_PASSWORD = get_env('DB_PASSWORD', 'pass')

def create_database():
    conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARSET utf8mb4;")
    conn.commit()
    cursor.close()
    conn.close()
    print(f"数据库 {DB_NAME} 初始化完成")

if __name__ == '__main__':
    create_database()