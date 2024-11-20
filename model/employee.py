from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DOUBLE
from dbconnect import Base
class EmployeeBase(BaseModel):
    userId: int

class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True, autoincrement=True)
    salary = Column(DOUBLE, nullable=True)
    startDate = Column(String(255), nullable=True)
    area = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)
    userId = Column(Integer, nullable=True)
