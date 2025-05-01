"""Add user sessions table for session management

Revision ID: add_user_sessions
Revises: add_account_lockout
Create Date: 2023-05-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_user_sessions'
down_revision = 'add_account_lockout'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_sessions table for session management
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(64), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('last_activity', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add index for faster queries on user_id and is_active
    op.create_index('idx_user_sessions_user_active', 'user_sessions', ['user_id', 'is_active'])
    
    # Add index on token for faster lookups
    op.create_index('idx_user_sessions_token', 'user_sessions', ['token'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_user_sessions_token')
    op.drop_index('idx_user_sessions_user_active')
    
    # Drop user_sessions table
    op.drop_table('user_sessions') 