"""Fix datetime timezone across all tables

Revision ID: e738192a
Revises: 2ff1d7b42ce0
Create Date: 2026-08-29 17:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e738192a'
down_revision: Union[str, Sequence[str], None] = '2ff1d7b42ce0'
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to TIMESTAMP WITH TIME ZONE across all tables."""
    # incidents
    op.alter_column('incidents', 'timestamp',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="timestamp AT TIME ZONE 'UTC'")
    op.alter_column('incidents', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")
    op.alter_column('incidents', 'updated_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="updated_at AT TIME ZONE 'UTC'")

    # users
    op.alter_column('users', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")
    op.alter_column('users', 'updated_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="updated_at AT TIME ZONE 'UTC'")

    # ais_tracks
    op.alter_column('ais_tracks', 'timestamp',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="timestamp AT TIME ZONE 'UTC'")
    op.alter_column('ais_tracks', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")

    # attribution_scores
    op.alter_column('attribution_scores', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")

    # drift_results
    op.alter_column('drift_results', 'origin_time_estimate',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=True,
                    postgresql_using="origin_time_estimate AT TIME ZONE 'UTC'")
    op.alter_column('drift_results', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")

    # ml_inference_log
    op.alter_column('ml_inference_log', 'timestamp',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="timestamp AT TIME ZONE 'UTC'")

    # slick_detections
    op.alter_column('slick_detections', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")

    # vessels
    op.alter_column('vessels', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")
    op.alter_column('vessels', 'updated_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False,
                    postgresql_using="updated_at AT TIME ZONE 'UTC'")

    # satellite_scenes column nullability & JSONB type alignment
    op.alter_column('satellite_scenes', 'source', existing_type=sa.String(), nullable=False)
    op.alter_column('satellite_scenes', 'scene_id', existing_type=sa.String(), nullable=False)
    op.alter_column('satellite_scenes', 'polarization', existing_type=sa.String(), nullable=True)
    op.alter_column('satellite_scenes', 'scene_metadata', existing_type=sa.JSON(), type_=postgresql.JSONB(), postgresql_using="scene_metadata::jsonb")


def downgrade() -> None:
    """Downgrade schema to TIMESTAMP WITHOUT TIME ZONE across all tables."""
    # vessels
    op.alter_column('vessels', 'updated_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="updated_at AT TIME ZONE 'UTC'")
    op.alter_column('vessels', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")

    # slick_detections
    op.alter_column('slick_detections', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")

    # ml_inference_log
    op.alter_column('ml_inference_log', 'timestamp',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="timestamp AT TIME ZONE 'UTC'")

    # drift_results
    op.alter_column('drift_results', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")
    op.alter_column('drift_results', 'origin_time_estimate',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=True,
                    postgresql_using="origin_time_estimate AT TIME ZONE 'UTC'")

    # attribution_scores
    op.alter_column('attribution_scores', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")

    # ais_tracks
    op.alter_column('ais_tracks', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")
    op.alter_column('ais_tracks', 'timestamp',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="timestamp AT TIME ZONE 'UTC'")

    # users
    op.alter_column('users', 'updated_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="updated_at AT TIME ZONE 'UTC'")
    op.alter_column('users', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")

    # incidents
    op.alter_column('incidents', 'updated_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="updated_at AT TIME ZONE 'UTC'")
    op.alter_column('incidents', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="created_at AT TIME ZONE 'UTC'")
    op.alter_column('incidents', 'timestamp',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False,
                    postgresql_using="timestamp AT TIME ZONE 'UTC'")
