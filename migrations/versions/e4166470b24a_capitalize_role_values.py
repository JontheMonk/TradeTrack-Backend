"""capitalize_role_values

Revision ID: e4166470b24a
Revises: 6ca5964dcda6
Create Date: 2025-12-28 16:00:57.684085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4166470b24a'
down_revision: Union[str, Sequence[str], None] = '6ca5964dcda6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint('employees_role_check', 'employees', type_='check')
    
    op.execute("UPDATE employees SET role = 'Admin' WHERE role = 'admin'")
    op.execute("UPDATE employees SET role = 'Employee' WHERE role = 'employee'")
    
    op.create_check_constraint(
        'employees_role_check',
        'employees',
        "role IN ('Admin', 'Employee')"
    )

def downgrade():
    op.drop_constraint('employees_role_check', 'employees', type_='check')
    
    op.execute("UPDATE employees SET role = 'admin' WHERE role = 'Admin'")
    op.execute("UPDATE employees SET role = 'employee' WHERE role = 'Employee'")
    
    op.create_check_constraint(
        'employees_role_check',
        'employees',
        "role IN ('admin', 'employee')"
    )
