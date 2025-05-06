"""
Create violation_status_log table

Revision ID: 20240610_status_log
Revises: 20240610_add_status
Create Date: 2024-06-10
"""
from alembic import op
import sqlalchemy as sa

revision = '20240610_status_log'
down_revision = '20240610_add_status'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'violation_status_log',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('violation_id', sa.Integer, sa.ForeignKey('violations.id'), nullable=False),
        sa.Column('old_status', sa.String(length=64), nullable=False),
        sa.Column('new_status', sa.String(length=64), nullable=False),
        sa.Column('changed_by', sa.String(length=128), nullable=False),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )

def downgrade():
    op.drop_table('violation_status_log') 