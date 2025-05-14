import os
from fastapi import FastAPI
from dotenv import load_dotenv
from . import routes

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)

app = FastAPI(title="Approval Service", description="审批流管理服务", version="0.1.0")

app.include_router(routes.router)