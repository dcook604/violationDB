"""
Add status column to violations table

Revision ID: 20240610_add_status
Revises: add_user_sessions
Create Date: 2024-06-10
"""
from alembic import op
import sqlalchemy as sa

revision = '20240610_add_status'
down_revision = 'add_user_sessions'
branch_labels = None
depends_on = None

def upgrade():
    # op.add_column('violations', sa.Column('status', sa.String(length=64), nullable=False, server_default='Open'))
    pass

def downgrade():
    op.drop_column('violations', 'status') 