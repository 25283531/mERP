from sqlalchemy.orm import Session
from typing import List, Optional

from ..models import models
from .. import schemas

def get_plan(db: Session, plan_id: int) -> Optional[models.Plan]:
    return db.query(models.Plan).filter(models.Plan.id == plan_id).first()

def get_plans(db: Session, skip: int = 0, limit: int = 100) -> List[models.Plan]:
    return db.query(models.Plan).offset(skip).limit(limit).all()

def create_plan(db: Session, plan: schemas.PlanCreate) -> models.Plan:
    db_plan = models.Plan(
        name=plan.name,
        start_time=plan.start_time,
        end_time=plan.end_time,
        quantity=plan.quantity
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, plan_id: int, plan_update: schemas.PlanUpdate) -> Optional[models.Plan]:
    db_plan = get_plan(db, plan_id)
    if db_plan:
        update_data = plan_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_plan, key, value)
        db.commit()
        db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: int) -> Optional[models.Plan]:
    db_plan = get_plan(db, plan_id)
    if db_plan:
        db.delete(db_plan)
        db.commit()
    return db_plan