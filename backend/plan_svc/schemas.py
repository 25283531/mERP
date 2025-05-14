from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PlanBase(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    quantity: float

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    quantity: Optional[float] = None

class PlanInDBBase(PlanBase):
    id: int

    class Config:
        orm_mode = True

class Plan(PlanInDBBase):
    pass

class PlanInDB(PlanInDBBase):
    pass