import os
import sys
import subprocess
import logging
import time
import socket
import requests
from pathlib import Path
from typing import Dict, List, Optional
from requests.exceptions import RequestException

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'backend.log'))
    ]
)
logger = logging.getLogger('backend_starter')

# 设置项目根目录到PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

# 导入数据库配置
try:
    from db_config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DEFAULT_DB_NAME, SERVICE_DB_NAMES, log_db_info
    # 设置环境变量，确保其他模块可以通过os.environ获取
    os.environ.setdefault('DB_USER', DB_USER)
    os.environ.setdefault('DB_PASSWORD', DB_PASSWORD)
    os.environ.setdefault('DB_HOST', DB_HOST)
    os.environ.setdefault('DB_PORT', str(DB_PORT))
    os.environ.setdefault('DB_NAME', DEFAULT_DB_NAME)
    logger.info("成功导入数据库配置")
    log_db_info()
except ImportError:
    logger.warning("无法导入db_config.py，将使用默认配置")
    # 添加数据库环境变量默认值
    os.environ.setdefault('DB_USER', 'root')
    os.environ.setdefault('DB_PASSWORD', 'password')
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_PORT', '3306')
    
    # 为各个微服务添加数据库名称环境变量
    os.environ.setdefault('DB_NAME', 'merp_db')  # 默认数据库名
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

# 服务配置
SERVICES = {
    'plan_svc': {
        'port': 8001,
        'description': '生产计划服务'
    },
    'order_svc': {
        'port': 8002,
        'description': '订单服务'
    },
    'approval_svc': {
        'port': 8003,
        'description': '审批服务'
    },
    'inventory_svc': {
        'port': 8004,
        'description': '库存服务'
    },
    'material_svc': {
        'port': 8005,
        'description': '物料服务'
    },
    'config_svc': {
        'port': 8006,
        'description': '配置服务'
    },
    'scheduler_svc': {
        'port': 8007,
        'description': '调度服务'
    },
    'shift_svc': {
        'port': 8008,
        'description': '班次服务'
    }
}


def start_service(service_name: str, port: int) -> Optional[subprocess.Popen]:
    """
    启动指定的微服务
    
    Args:
        service_name: 服务名称
        port: 服务端口
        
    Returns:
        subprocess.Popen: 启动的进程对象，如果启动失败则返回None
    """
    service_dir = os.path.join(os.path.dirname(__file__), service_name)
    
    if not os.path.exists(service_dir):
        logger.error(f"服务目录不存在: {service_dir}")
        return None
        
    app_path = os.path.join(service_dir, 'app.py')
    if not os.path.exists(app_path):
        logger.error(f"服务入口文件不存在: {app_path}")
        return None
    
    # 检查端口是否被占用
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
    except socket.error:
        logger.error(f"端口 {port} 已被占用，无法启动服务 {service_name}")
        return None
    finally:
        sock.close()
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{root_dir};{env.get('PYTHONPATH', '')}"
        env['SERVICE_PORT'] = str(port)
        
        # 设置服务特定的数据库名称
        if service_name in SERVICE_DB_NAMES:
            env['DB_NAME'] = SERVICE_DB_NAMES[service_name]
            logger.info(f"为服务 {service_name} 设置数据库名称: {SERVICE_DB_NAMES[service_name]}")
        else:
            logger.warning(f"服务 {service_name} 没有配置特定的数据库名称，使用默认值")
        
        # 检查依赖文件
        requirements_path = os.path.join(service_dir, 'requirements.txt')
        if os.path.exists(requirements_path):
            logger.info(f"检查 {service_name} 的依赖项...")
            # 这里可以添加依赖检查逻辑，但为了简化，暂不实现
        
        # 启动服务 - 使用模块路径格式启动，避免相对导入问题
        module_path = f'backend.{service_name}.app:app'
        cmd = [sys.executable, '-m', 'uvicorn', module_path, '--reload', f'--port={port}']
        process = subprocess.Popen(
            cmd,
            cwd=service_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 等待短暂时间，检查进程是否立即退出（表示启动失败）
        import time
        time.sleep(0.5)
        if process.poll() is not None:
            logger.error(f"服务 {service_name} 启动失败，进程立即退出，退出码: {process.returncode}")
            return None
        
        logger.info(f"已启动服务 {service_name} 在端口 {port}")
        return process
    except Exception as e:
        logger.error(f"启动服务 {service_name} 失败: {str(e)}")
        return None


def monitor_processes(processes: Dict[str, subprocess.Popen]) -> None:
    """
    监控所有服务进程的输出
    
    Args:
        processes: 服务名称到进程对象的映射
    """
    import time
    import threading
    import queue

    def enqueue_output(out, q, service_name, stream_name):
        try:
            for line in iter(out.readline, ''):
                if not line: # Check for empty line which might indicate EOF
                    break
                q.put((service_name, stream_name, line))
        except ValueError: # Handle cases where the stream is closed
            pass # Stream closed, exiting thread
        finally:
            out.close()
    
    output_queue = queue.Queue()
    threads = []

    for service_name, process in processes.items():
        # stdout thread
        t_stdout = threading.Thread(target=enqueue_output, args=(process.stdout, output_queue, service_name, 'stdout'))
        t_stdout.daemon = True
        t_stdout.start()
        threads.append(t_stdout)

        # stderr thread
        t_stderr = threading.Thread(target=enqueue_output, args=(process.stderr, output_queue, service_name, 'stderr'))
        t_stderr.daemon = True
        t_stderr.start()
        threads.append(t_stderr)

    try:
        while processes:
            # 检查所有进程是否仍在运行
            active_processes = {}
            for service_name, process in list(processes.items()):
                if process.poll() is None:
                    active_processes[service_name] = process
                else:
                    logger.warning(f"服务 {service_name} 已退出，退出码: {process.returncode}")
                    # 确保所有输出都被读取
                    while not output_queue.empty():
                        try:
                            s_name, stream_name, line = output_queue.get_nowait()
                            line = line.strip()
                            if line:
                                if s_name == service_name: # Log output for the exited process
                                    if stream_name == 'stdout':
                                        logger.info(f"{s_name}: {line}")
                                    else:
                                        logger.error(f"{s_name} 错误: {line}")
                        except queue.Empty:
                            break # Queue is empty
            processes = active_processes
            if not processes and output_queue.empty(): # All processes exited and queue is empty
                break

            # 处理队列中的输出
            try:
                service_name, stream_name, line = output_queue.get(timeout=0.1)
                line = line.strip()
                if line:
                    if stream_name == 'stdout':
                        logger.info(f"{service_name}: {line}")
                    else:
                        logger.error(f"{service_name} 错误: {line}")
            except queue.Empty:
                pass # No output in queue, continue
            
            time.sleep(0.01) # Shorter sleep to be more responsive
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在关闭所有服务...")
        for service_name, process in processes.items():
            logger.info(f"正在关闭服务 {service_name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"服务 {service_name} 未能在5秒内关闭，强制终止")
                process.kill()
        logger.info("所有服务已关闭")


def check_service_health(service_name: str, port: int) -> bool:
    """
    检查服务健康状态
    
    Args:
        service_name: 服务名称
        port: 服务端口
        
    Returns:
        bool: 服务是否健康
    """
    try:
        # 尝试访问服务的健康检查端点
        url = f"http://localhost:{port}/health"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            logger.info(f"服务 {service_name} 健康检查通过")
            return True
        elif response.status_code == 404:
            # 如果健康检查端点不存在（404），尝试访问根路径
            logger.info(f"服务 {service_name} 没有健康检查端点，尝试访问根路径")
            root_url = f"http://localhost:{port}/"
            root_response = requests.get(root_url, timeout=2)
            if root_response.status_code < 500:  # 任何非服务器错误都视为服务在运行
                logger.info(f"服务 {service_name} 根路径可访问，视为健康")
                return True
            else:
                logger.warning(f"服务 {service_name} 返回服务器错误，状态码: {root_response.status_code}")
                return False
        else:
            logger.warning(f"服务 {service_name} 健康检查失败，状态码: {response.status_code}")
            return False
    except RequestException as e:
        # 如果服务没有健康检查端点或无法连接，尝试访问根路径
        logger.info(f"访问服务 {service_name} 健康检查端点失败: {str(e)}，尝试访问根路径")
        try:
            url = f"http://localhost:{port}/"
            response = requests.get(url, timeout=2)
            if response.status_code < 500:  # 任何非服务器错误都视为服务在运行
                logger.info(f"服务 {service_name} 可访问，视为健康")
                return True
            else:
                logger.warning(f"服务 {service_name} 返回服务器错误，状态码: {response.status_code}")
                return False
        except RequestException as e:
            logger.warning(f"服务 {service_name} 不可访问: {str(e)}")
            return False

def main():
    """
    主函数，启动所有微服务
    """
    logger.info("开始启动后端服务...")
    
    # 定义服务启动顺序（优先启动基础服务）
    service_order = [
        'config_svc',      # 配置服务优先启动
        'scheduler_svc',   # 调度服务
        'approval_svc',    # 审批服务
        'material_svc',    # 物料服务
        'inventory_svc',   # 库存服务
        'order_svc',       # 订单服务
        'plan_svc',        # 计划服务
        'shift_svc'        # 班次服务
    ]
    
    # 验证所有服务都在配置中
    for service_name in service_order:
        if service_name not in SERVICES:
            logger.error(f"服务 {service_name} 在启动顺序中定义但未在SERVICES配置中找到")
            return
    
    # 检查是否有未在启动顺序中定义的服务
    for service_name in SERVICES:
        if service_name not in service_order:
            logger.warning(f"服务 {service_name} 在SERVICES配置中但未在启动顺序中定义，将在最后启动")
            service_order.append(service_name)
    
    # 按顺序启动服务
    processes = {}
    for service_name in service_order:
        config = SERVICES[service_name]
        logger.info(f"正在启动 {service_name} ({config['description']}) 在端口 {config['port']}...")
        process = start_service(service_name, config['port'])
        if process:
            processes[service_name] = process
            # 给关键服务一些启动时间
            if service_name in ['config_svc', 'scheduler_svc', 'approval_svc']:
                logger.info(f"等待 {service_name} 完全启动...")
                time.sleep(3)
                # 进行健康检查
                health_status = check_service_health(service_name, config['port'])
                if not health_status:
                    logger.warning(f"服务 {service_name} 可能未正常启动，但将继续启动其他服务")
    
    if not processes:
        logger.error("没有成功启动任何服务，退出程序")
        return
    
    logger.info(f"成功启动了 {len(processes)} 个服务")
    
    # 监控所有进程
    monitor_processes(processes)


if __name__ == "__main__":
    main()