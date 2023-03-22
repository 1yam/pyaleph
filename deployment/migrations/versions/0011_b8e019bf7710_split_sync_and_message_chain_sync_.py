"""split sync and message chain sync statuses

Revision ID: b8e019bf7710
Revises: 8a5eaab15d40
Create Date: 2023-03-08 14:48:26.581627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b8e019bf7710"
down_revision = "8a5eaab15d40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Add the new type column
    op.add_column("chains_sync_status", sa.Column("type", sa.String(), nullable=True))
    # We only support message events on Tezos, every other chain connector fetches sync events
    op.execute("update chains_sync_status set type = 'sync' where chain != 'TEZOS'")
    op.execute("update chains_sync_status set type = 'message' where chain = 'TEZOS'")
    op.alter_column("chains_sync_status", "type", nullable=False)

    # Recreate the primary key
    op.drop_constraint("chains_sync_status_pkey", "chains_sync_status", type_="primary")
    op.create_primary_key(
        "chains_sync_status_pkey", "chains_sync_status", ["chain", "type"]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("chains_sync_status_pkey", "chains_sync_status", type_="primary")
    op.drop_column("chains_sync_status", "type")
    op.create_primary_key(
        "chains_sync_status_pkey",
        "chains_sync_status",
        ["chain"],
    )
    # ### end Alembic commands ###