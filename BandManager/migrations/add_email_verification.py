"""Add email verification table

Revision ID: add_email_verification
Revises: 
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_email_verification'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 创建邮箱验证表
    op.create_table('email_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('verification_type', sa.String(length=20), nullable=False, default='register'),
        sa.Column('is_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_email_verifications_email', 'email_verifications', ['email'])

def downgrade():
    # 删除索引
    op.drop_index('ix_email_verifications_email', table_name='email_verifications')
    
    # 删除表
    op.drop_table('email_verifications')
