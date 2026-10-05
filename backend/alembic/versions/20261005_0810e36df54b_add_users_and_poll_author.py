"""add users and poll author

Revision ID: 0810e36df54b
Revises: 20f2abb78dc2
Create Date: 2026-10-05 13:37:44.202237
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0810e36df54b"
down_revision: str | None = "20f2abb78dc2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.add_column("polls", sa.Column("author_id", sa.Uuid(), nullable=True))
    op.create_index(op.f("ix_polls_author_id"), "polls", ["author_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_polls_author_id_users"),
        "polls",
        "users",
        ["author_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_polls_author_id_users"), "polls", type_="foreignkey")
    op.drop_index(op.f("ix_polls_author_id"), table_name="polls")
    op.drop_column("polls", "author_id")
    op.drop_table("users")
