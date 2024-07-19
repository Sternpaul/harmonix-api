"""Add campaigns, tvl, reward_threshold

Revision ID: c60cbeb13f60
Revises: e44b0c50293a
Create Date: 2024-07-17 12:35:21.535303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from core import constants


# revision identifiers, used by Alembic.
revision: str = 'c60cbeb13f60'
down_revision: Union[str, None] = 'e44b0c50293a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('campaigns',
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reward_thresholds',
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('tier', sa.Integer(), nullable=False),
    sa.Column('threshold', sa.Float(), nullable=False),
    sa.Column('commission_rate', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_monthly_tvl',
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('month', sa.DateTime(), nullable=False),
    sa.Column('total_value_locked', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_monthly_tvl_month'), 'user_monthly_tvl', ['month'], unique=False)
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('users', sa.Column('tier', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=constants.UserTier.DEFAULT.value))
    op.add_column('rewards', sa.Column('campaign_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default="default"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'tier')
    op.drop_column('rewards', 'campaign_name')
    op.drop_index(op.f('ix_user_monthly_tvl_month'), table_name='user_monthly_tvl')
    op.drop_table('user_monthly_tvl')
    op.drop_table('reward_thresholds')
    op.drop_table('campaigns')
    # ### end Alembic commands ###
