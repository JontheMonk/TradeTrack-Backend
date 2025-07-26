from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)
    role = Column(String, nullable=False, default="user")
