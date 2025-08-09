from sqlalchemy import Column, String, Float, CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from db import Base

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)
    role = Column(String, nullable=False, default="employee")

    __table_args__ = (
        CheckConstraint("role = ANY (ARRAY['admin', 'employee'])", name="employees_role_check"),
    )
