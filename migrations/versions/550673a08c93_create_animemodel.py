"""Create AnimeModel

Revision ID: 550673a08c93
Revises: 
Create Date: 2021-10-11 13:41:43.068145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '550673a08c93'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('animes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('synopsis', sa.String(length=1023), nullable=False),
    sa.Column('image_url', sa.String(length=255), nullable=False),
    sa.Column('total_episodes', sa.Integer(), nullable=False),
    sa.Column('is_movie', sa.Boolean(), nullable=False),
    sa.Column('is_dubbed', sa.Boolean(), nullable=False),
    sa.Column('is_completed', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('animes')
    # ### end Alembic commands ###