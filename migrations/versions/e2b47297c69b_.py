"""empty message

Revision ID: e2b47297c69b
Revises: cd6d05ad3395
Create Date: 2019-01-18 16:30:39.031485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2b47297c69b'
down_revision = 'cd6d05ad3395'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('story', sa.Column('fb_comments', sa.Integer(), nullable=True))
    op.add_column('story', sa.Column('fb_shares', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('story', 'fb_shares')
    op.drop_column('story', 'fb_comments')
    # ### end Alembic commands ###
