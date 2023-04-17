"""file size not null

Revision ID: 039c56d3b33e
Revises: daa92b500049
Create Date: 2023-04-13 17:13:01.353182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "039c56d3b33e"
down_revision = "daa92b500049"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("files", "size", existing_type=sa.BIGINT(), nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("files", "size", existing_type=sa.BIGINT(), nullable=True)
    # ### end Alembic commands ###