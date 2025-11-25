"""
SQLAlchemy model representing an employee record in the system.

This model stores identity information, role-based access classification,
and the employee's facial embedding used for biometric verification.

Notes
-----
- Embeddings are stored as a 512-dimensional float array for now.
  A migration to PGVector is recommended for efficient similarity search.
- `created_at` and `updated_at` timestamps are managed entirely by the
  database (server-side defaults).
- Role values are constrained at the database level to ensure data integrity.
"""

from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    CheckConstraint,
    func
)
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base


class Employee(Base):
    """
    ORM model for the `employees` table.

    Attributes
    ----------
    employee_id : str
        Unique identifier for the employee. This is the primary key and is
        used everywhere in the system to reference the employee.
    name : str
        Display name for UI and admin dashboards. Required.
    embedding : list[float]
        512-dimensional normalized face embedding used to verify identity.
        Stored as a PostgreSQL float array.
    role : str
        Role determining the user's permissions (`"admin"` or `"employee"`).
        Validated via a database CHECK constraint.
    created_at : datetime
        Timestamp indicating when the employee record was created.
        Automatically assigned by the database.
    updated_at : datetime
        Timestamp updated on each UPDATE operation.
        Managed automatically by the database.
    """

    __tablename__ = "employees"

    # ------------------------------------------------------------------
    # Primary fields
    # ------------------------------------------------------------------

    employee_id = Column(
        String,
        primary_key=True,
        doc="Unique system-wide identifier for the employee."
    )

    name = Column(
        String,
        nullable=False,
        doc="Human-readable display name."
    )

    # ------------------------------------------------------------------
    # Biometric data
    # ------------------------------------------------------------------

    embedding = Column(
        ARRAY(Float),
        nullable=False,
        doc="512-dimensional face embedding used for matching."
    )

    # ------------------------------------------------------------------
    # Role-based access control
    # ------------------------------------------------------------------

    role = Column(
        String,
        nullable=False,
        default="employee",
        doc="Access role (`admin` or `employee`)."
    )

    # ------------------------------------------------------------------
    # Auditing metadata
    # ------------------------------------------------------------------

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        doc="Server-side timestamp of record creation."
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="Server-side timestamp of last update."
    )

    # ------------------------------------------------------------------
    # Table constraints
    # ------------------------------------------------------------------

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'employee')",
            name="employees_role_check"
        ),
    )
