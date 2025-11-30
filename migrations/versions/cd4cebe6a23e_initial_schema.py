"""initial schema

Revision ID: cd4cebe6a23e
Revises:
Create Date: 2025-11-27 21:28:00.354071
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cd4cebe6a23e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema"""
    op.create_table(
        'employees',
        sa.Column('employee_id', sa.String(128), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        
        sa.Column(
            'embedding',
            postgresql.ARRAY(sa.Float()).with_variant(sa.JSON(), 'sqlite'),
            nullable=False
        ),

        sa.Column('role', sa.String(32), nullable=False),

        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),

        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            server_onupdate=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),

        sa.CheckConstraint(
            "role IN ('admin', 'employee')",
            name='employees_role_check'
        ),

        sa.PrimaryKeyConstraint('employee_id')
    )

    op.create_index("ix_employees_name", "employees", ["name"])
    op.create_index("ix_employees_role", "employees", ["role"])



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('employees')
