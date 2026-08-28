"""Drop timestamp column from satellite_scenes table

Revision ID: 2ff1d7b42ce0
Revises: f9d3c7d842be
Create Date: 2026-08-28 22:51:52.749432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2ff1d7b42ce0'
down_revision: Union[str, Sequence[str], None] = 'f9d3c7d842be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the timestamp column that was replaced by acquisition_time
    op.drop_column('satellite_scenes', 'timestamp')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the timestamp column (as nullable for safety)
    op.add_column('satellite_scenes', sa.Column('timestamp', sa.DateTime(), nullable=True))