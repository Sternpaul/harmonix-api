"""add_reward_distribution_config

Revision ID: f46b7c39954a
Revises: ff101077736c
Create Date: 2024-12-21 15:51:56.675895

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "f46b7c39954a"
down_revision: Union[str, None] = "ff101077736c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.create_table(
        "reward_distribution_config",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("vault_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("reward_token", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("total_reward", sa.Float(), nullable=True),
        sa.Column("week", sa.Integer(), nullable=True),
        sa.Column("distribution_percentage", sa.Float(), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["vault_id"],
            ["vaults.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="config",
    )
    op.create_index(
        op.f("ix_config_reward_distribution_config_created_at"),
        "reward_distribution_config",
        ["created_at"],
        unique=False,
        schema="config",
    )
    op.create_index(
        op.f("ix_config_reward_distribution_config_start_date"),
        "reward_distribution_config",
        ["start_date"],
        unique=False,
        schema="config",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_config_reward_distribution_config_start_date"),
        table_name="reward_distribution_config",
        schema="config",
    )
    op.drop_index(
        op.f("ix_config_reward_distribution_config_created_at"),
        table_name="reward_distribution_config",
        schema="config",
    )
    op.drop_table("reward_distribution_config", schema="config")
    # ### end Alembic commands ###
