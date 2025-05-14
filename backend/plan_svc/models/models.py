from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    quantity = Column(Float)

    def __repr__(self):
        return f"<Plan(id={self.id}, name='{self.name}')>"