from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import SessionLocal, engine # Updated import
from models import models
from routes import router as plan_router # Updated import
from schemas import Plan # Assuming Plan schema might be useful here, adjust as needed

# Create database tables
models.Base.metadata.create_all(bind=engine)

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

# The following is for running with uvicorn directly, e.g., uvicorn plan_svc.app:app --reload --port 5001
# Ensure uvicorn is installed: pip install uvicorn[standard]
# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5001) # Port can be configured as needed