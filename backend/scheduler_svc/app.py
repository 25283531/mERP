import os
import sys
from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv

# 设置项目根目录到PYTHONPATH
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

# 使用绝对导入
from backend.scheduler_svc.routes import router

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)

app = FastAPI(title="Scheduler Service", description="调度服务", version="0.1.0")

app.include_router(router)

@app.get("/", tags=["Root"], summary="Root endpoint for service health check")
def read_root():
    return {"message": f"Hello from {app.title}!"}

@app.get("/health", tags=["Health"], summary="Health check endpoint")
def health_check():
    return {"status": "ok", "service": app.title}