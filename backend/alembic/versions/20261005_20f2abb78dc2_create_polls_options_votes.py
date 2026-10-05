"""create polls options votes

Revision ID: 20f2abb78dc2
Revises:
Create Date: 2026-10-05 12:59:11.178926
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20f2abb78dc2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "polls",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("question", sa.String(length=200), nullable=False),
        sa.Column("closes_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_polls")),
    )
    op.create_index(op.f("ix_polls_created_at"), "polls", ["created_at"], unique=False)
    op.create_table(
        "options",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("poll_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["poll_id"], ["polls.id"], name=op.f("fk_options_poll_id_polls"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_options")),
        sa.UniqueConstraint("poll_id", "position", name=op.f("uq_options_poll_id_position")),
    )
    op.create_index(op.f("ix_options_poll_id"), "options", ["poll_id"], unique=False)
    op.create_table(
        "votes",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("option_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["option_id"],
            ["options.id"],
            name=op.f("fk_votes_option_id_options"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_votes")),
    )
    op.create_index(op.f("ix_votes_option_id"), "votes", ["option_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_votes_option_id"), table_name="votes")
    op.drop_table("votes")
    op.drop_index(op.f("ix_options_poll_id"), table_name="options")
    op.drop_table("options")
    op.drop_index(op.f("ix_polls_created_at"), table_name="polls")
    op.drop_table("polls")
