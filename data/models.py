"""
SQLAlchemy ORM model definitions.

This module defines:
    • The single shared declarative Base used by all ORM models.
    • The Employee model representing user identity + face embeddings.

Every table created by SQLAlchemy comes from Base.metadata.
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    CheckConstraint,
    ForeignKey,
    JSON,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY

# ---------------------------------------------------------------------------
# Global declarative Base shared across the entire application
# ---------------------------------------------------------------------------

Base = declarative_base()


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------

class Employee(Base):
    """
    ORM model representing an employee record in the database.

    Stores:
        • a unique employee ID
        • display name
        • normalized 512-dimensional face embedding
        • role for access control
        • automatic creation/update timestamps

    Embedding storage:
        PostgreSQL:
            ARRAY(Float)
        SQLite (tests):
            JSON
        The .with_variant(JSON, "sqlite") makes the model database-agnostic.
    """

    __tablename__ = "employees"

    employee_id = Column(
        String(128),
        primary_key=True,
        doc="Unique employee identifier used across the system."
    )

    name = Column(
        String(256),
        nullable=False,
        doc="Human-readable display name."
    )

    embedding = Column(
        ARRAY(Float).with_variant(JSON, "sqlite"),
        nullable=False,
        doc="512-dimensional face embedding used for biometric verification."
    )

    role = Column(
        String(32),
        nullable=False,
        default="employee",
        doc="Access role (`admin` or `employee`)."
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        doc="Timestamp when the employee was first created."
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="Timestamp updated automatically whenever the record changes."
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'employee')",
            name="employees_role_check"
        ),
    )

class TimeEntry(Base):
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(128), ForeignKey("employees.employee_id"), nullable=False)
    clock_in = Column(DateTime, nullable=False, server_default=func.now())
    clock_out = Column(DateTime, nullable=True)
