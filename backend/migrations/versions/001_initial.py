"""initial

Revision ID: 001
Revises: 
Create Date: 2026-08-27 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2.types import Geometry

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. incidents
    op.create_table(
        'incidents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('location', Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incidents_timestamp'), 'incidents', ['timestamp'], unique=False)
    # Spatial index for PostGIS geometry column
    op.create_index('ix_incidents_location', 'incidents', ['location'], postgresql_using='gist')

    # 3. satellite_scenes
    op.create_table(
        'satellite_scenes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('satellite', sa.String(), nullable=False),
        sa.Column('product_type', sa.String(), nullable=False),
        sa.Column('polarization', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('bbox', Geometry(geometry_type='POLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # Spatial index for PostGIS geometry column
    op.create_index('ix_scenes_bbox', 'satellite_scenes', ['bbox'], postgresql_using='gist')

    # 4. slick_detections
    op.create_table(
        'slick_detections',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('incident_id', sa.UUID(), nullable=False),
        sa.Column('scene_id', sa.UUID(), nullable=True),
        sa.Column('geometry', Geometry(geometry_type='POLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('area_km2', sa.Float(), nullable=False),
        sa.Column('length_km', sa.Float(), nullable=True),
        sa.Column('width_km', sa.Float(), nullable=True),
        sa.Column('orientation_deg', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('age_estimate_hours', sa.Float(), nullable=True),
        sa.Column('age_confidence', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scene_id'], ['satellite_scenes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    # Spatial index for PostGIS geometry column
    op.create_index('ix_slick_detections_geometry', 'slick_detections', ['geometry'], postgresql_using='gist')

    # 5. drift_results
    op.create_table(
        'drift_results',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('incident_id', sa.UUID(), nullable=False),
        sa.Column('origin_point', Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('origin_probability_cone', Geometry(srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('origin_time_estimate', sa.DateTime(), nullable=True),
        sa.Column('origin_confidence', sa.Float(), nullable=True),
        sa.Column('hindcast_path', Geometry(srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('forecast_path', Geometry(srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('model_name', sa.String(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    # Spatial index for PostGIS geometry column (origin_point as per PRD §26)
    op.create_index('ix_drift_results_origin_point', 'drift_results', ['origin_point'], postgresql_using='gist')

    # 6. vessels
    op.create_table(
        'vessels',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('mmsi', sa.String(), nullable=False),
        sa.Column('imo', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('flag', sa.String(), nullable=True),
        sa.Column('length', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vessels_mmsi'), 'vessels', ['mmsi'], unique=True)

    # 7. ais_tracks
    op.create_table(
        'ais_tracks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vessel_id', sa.UUID(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('position', Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('course', sa.Float(), nullable=True),
        sa.Column('heading', sa.Float(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vessel_id'], ['vessels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ais_tracks_timestamp'), 'ais_tracks', ['timestamp'], unique=False)
    # Spatial index for PostGIS geometry column
    op.create_index('ix_ais_tracks_position', 'ais_tracks', ['position'], postgresql_using='gist')

    # 8. attribution_scores
    op.create_table(
        'attribution_scores',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('incident_id', sa.UUID(), nullable=False),
        sa.Column('vessel_id', sa.UUID(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('proximity_score', sa.Float(), nullable=False),
        sa.Column('temporality_score', sa.Float(), nullable=False),
        sa.Column('trajectory_score', sa.Float(), nullable=False),
        sa.Column('anomaly_score', sa.Float(), nullable=False),
        sa.Column('anomaly_flag', sa.Boolean(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vessel_id'], ['vessels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. ml_inference_log
    op.create_table(
        'ml_inference_log',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('service_name', sa.String(), nullable=False),
        sa.Column('request_payload', sa.JSON(), nullable=True),
        sa.Column('response_payload', sa.JSON(), nullable=True),
        sa.Column('model_name', sa.String(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('ml_inference_log')
    op.drop_table('attribution_scores')
    op.drop_index(op.f('ix_ais_tracks_timestamp'), table_name='ais_tracks')
    op.drop_table('ais_tracks')
    op.drop_index(op.f('ix_vessels_mmsi'), table_name='vessels')
    op.drop_table('vessels')
    op.drop_table('drift_results')
    op.drop_table('slick_detections')
    op.drop_table('satellite_scenes')
    op.drop_index(op.f('ix_incidents_timestamp'), table_name='incidents')
    op.drop_table('incidents')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
