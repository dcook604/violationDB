"""add_violation_reply_table

Revision ID: 5ed23f8a9b12
Revises: bb318ccc59c1
Create Date: 2025-05-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ed23f8a9b12'
down_revision = 'bb318ccc59c1'
branch_labels = None
depends_on = None


def upgrade():
    # Create violation_replies table
    op.create_table('violation_replies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('violation_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['violation_id'], ['violations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add index for faster lookups
    op.create_index(op.f('ix_violation_replies_violation_id'), 'violation_replies', ['violation_id'], unique=False)


def downgrade():
    # Drop index
    op.drop_index(op.f('ix_violation_replies_violation_id'), table_name='violation_replies')
    
    # Drop table
    op.drop_table('violation_replies') 