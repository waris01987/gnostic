"""Added roles and permissions

Revision ID: 54f12595d08b
Revises: 4774cc94d7b2
Create Date: 2024-10-21 13:13:59.169484

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "54f12595d08b"
down_revision: Union[str, None] = "4774cc94d7b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "organisations", sa.Column("profile_picture", sa.String(), nullable=True)
    )
    op.drop_constraint("permissions_role_id_fkey", "permissions", type_="foreignkey")
    op.drop_column("permissions", "role_id")
    op.add_column("role_permissions", sa.Column("uuid", sa.UUID(), nullable=False))
    op.add_column("role_permissions", sa.Column("role_id", sa.UUID(), nullable=False))
    op.create_foreign_key(None, "role_permissions", "roles", ["role_id"], ["uuid"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "role_permissions", type_="foreignkey")
    op.drop_column("role_permissions", "role_id")
    op.drop_column("role_permissions", "uuid")
    op.add_column(
        "permissions",
        sa.Column("role_id", sa.UUID(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "permissions_role_id_fkey", "permissions", "roles", ["role_id"], ["uuid"]
    )
    op.drop_column("organisations", "profile_picture")
    # ### end Alembic commands ###
