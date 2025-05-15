from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import os
import sys
from pathlib import Path

# 设置项目根目录到PYTHONPATH
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

# 导入本地模块
from backend.plan_svc.database import SessionLocal, engine
from backend.plan_svc.models.models import Base
from backend.plan_svc.routes import router as plan_router
from backend.plan_svc.schemas import Plan

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Plan Service API",
    description="API for managing production plans.",
    version="0.1.0"
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include the API router from routes.py
app.include_router(plan_router)

@app.get("/", tags=["Root"], summary="Root endpoint for service health check")
def read_root():
    return {"message": "Hello from Plan Service!"}

@app.get("/health", tags=["Health"], summary="Health check endpoint")
def health_check():
    return {"status": "ok", "service": "plan_service"}

# The following is for running with uvicorn directly, e.g., uvicorn plan_svc.app:app --reload --port 5001
# Ensure uvicorn is installed: pip install uvicorn[standard]
# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5001) # Port can be configured as needed