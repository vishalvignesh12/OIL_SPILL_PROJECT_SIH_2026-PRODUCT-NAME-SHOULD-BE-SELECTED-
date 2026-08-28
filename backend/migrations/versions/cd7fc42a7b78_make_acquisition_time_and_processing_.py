"""Make acquisition_time and processing_time timezone-aware

Revision ID: cd7fc42a7b78
Revises: 00560fe96b5e_add_satellite_ingestion_fields_to_.py
Create Date: 2026-08-28 22:44:54.332635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cd7fc42a7b78'
down_revision: Union[str, Sequence[str], None] = '00560fe96b5e_add_satellite_ingestion_fields_to_.py'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make acquisition_time and processing_time timezone-aware
    op.alter_column('satellite_scenes', 'acquisition_time',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=False)
    op.alter_column('satellite_scenes', 'processing_time',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert acquisition_time and processing_time to timezone-naive
    op.alter_column('satellite_scenes', 'processing_time',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   existing_nullable=True)
    op.alter_column('satellite_scenes', 'acquisition_time',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   existing_nullable=False)