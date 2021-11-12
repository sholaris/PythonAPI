"""add foreign key to posts table

Revision ID: 827d81953e1b
Revises: c24804134076
Create Date: 2021-11-11 22:55:18.118996

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '827d81953e1b'
down_revision = 'c24804134076'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key('posts_users_fk', 'posts', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    pass


def downgrade():
    op.drop_constraint('posts_users_fk', 'posts')
    op.drop_column('posts', 'user_id')
    pass
