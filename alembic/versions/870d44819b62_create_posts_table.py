"""create posts table

Revision ID: 870d44819b62
Revises: 
Create Date: 2021-11-11 22:40:27.443195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '870d44819b62'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "posts", 
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('published', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    pass


def downgrade():
    op.drop_table('posts')
    pass
