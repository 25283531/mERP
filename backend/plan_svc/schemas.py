from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PlanBase(BaseModel):
    name: str
    product_name: str
    notes: Optional[str] = None
    start_time: datetime
    end_time: datetime
    quantity: float

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    name: Optional[str] = None
    product_name: Optional[str] = None
    notes: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    quantity: Optional[float] = None

class PlanInDBBase(PlanBase):
    id: int

    class Config:
        from_attributes = True  # 替换已弃用的orm_mode配置

class Plan(PlanInDBBase):
    pass

class PlanInDB(PlanInDBBase):
    pass