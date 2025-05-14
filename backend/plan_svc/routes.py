from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from schemas import Plan, PlanCreate, PlanUpdate
from services import plan_service
from models import models
from .database import get_db # Import get_db from database.py

router = APIRouter(
    prefix="/api/v1/plans",
    tags=["plans"],
)

@router.post("/", response_model=schemas.Plan)
def create_new_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    return plan_service.create_plan(db=db, plan=plan)

@router.get("/", response_model=List[schemas.Plan])
def read_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    plans = plan_service.get_plans(db, skip=skip, limit=limit)
    return plans

@router.get("/{plan_id}", response_model=schemas.Plan)
def read_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = plan_service.get_plan(db, plan_id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.put("/{plan_id}", response_model=schemas.Plan)
def update_existing_plan(plan_id: int, plan_update: schemas.PlanUpdate, db: Session = Depends(get_db)):
    db_plan = plan_service.update_plan(db, plan_id=plan_id, plan_update=plan_update)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.delete("/{plan_id}", response_model=schemas.Plan)
def delete_existing_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = plan_service.delete_plan(db, plan_id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan