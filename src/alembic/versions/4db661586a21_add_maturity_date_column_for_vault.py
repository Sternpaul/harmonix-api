"""add maturity date column for vault

Revision ID: 4db661586a21
Revises: 2b992ca3cd44
Create Date: 2024-08-29 00:17:40.661275

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "4db661586a21"
down_revision: Union[str, None] = "2b992ca3cd44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "vaults",
        sa.Column("maturity_date", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("vaults", "maturity_date")
    # ### end Alembic commands ###
