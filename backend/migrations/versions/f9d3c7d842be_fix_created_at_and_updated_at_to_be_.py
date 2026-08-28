"""Fix created_at and updated_at to be timezone-aware

Revision ID: f9d3c7d842be
Revises: cd7fc42a7b78
Create Date: 2026-08-28 22:46:28.426618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f9d3c7d842be'
down_revision: Union[str, Sequence[str], None] = 'cd7fc42a7b78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fix created_at and updated_at to be timezone-aware
    op.alter_column('satellite_scenes', 'created_at',
                   existing_type=sa.DateTime(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=False)
    op.alter_column('satellite_scenes', 'updated_at',
                   existing_type=sa.DateTime(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert created_at and updated_at to timezone-naive
    op.alter_column('satellite_scenes', 'updated_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=sa.DateTime(),
                   existing_nullable=False)
    op.alter_column('satellite_scenes', 'created_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=sa.DateTime(),
                   existing_nullable=False)