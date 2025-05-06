"""Add account lockout and Argon2 password hashing support

Revision ID: add_account_lockout
Revises: violation_reply_table
Create Date: 2023-05-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_account_lockout'
down_revision = '5ed23f8a9b12'
branch_labels = None
depends_on = None


def upgrade():
    # Update the length of password_hash and temp_password columns
    op.alter_column('users', 'password_hash', type_=sa.String(255))
    op.alter_column('users', 'temp_password', type_=sa.String(255), nullable=True)
    
    # Add new columns for account lockout and password algorithm
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('last_failed_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('account_locked_until', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('password_algorithm', sa.String(20), nullable=True, server_default='werkzeug'))
    
    # Set default values for new columns
    op.execute("UPDATE users SET failed_login_attempts = 0")
    op.execute("UPDATE users SET password_algorithm = 'werkzeug'")


def downgrade():
    # Remove columns added for account lockout
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'last_failed_login')
    op.drop_column('users', 'account_locked_until')
    op.drop_column('users', 'password_algorithm')
    
    # Revert column lengths
    op.alter_column('users', 'password_hash', type_=sa.String(128))
    op.alter_column('users', 'temp_password', type_=sa.String(128), nullable=True) 