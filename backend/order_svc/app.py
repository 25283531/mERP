import os
from fastapi import FastAPI
from dotenv import load_dotenv
from . import routes

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)

app = FastAPI(title="Order Service", description="出货申请与审批服务", version="0.1.0")

app.include_router(routes.router)