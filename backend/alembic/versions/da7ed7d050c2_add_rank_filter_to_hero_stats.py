"""add rank filter to hero stats

Revision ID: da7ed7d050c2
Revises: 1bf10179c3a5
Create Date: 2026-06-11 18:09:20.590500

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision = "da7ed7d050c2"
down_revision: Union[str, Sequence[str], None] = "1bf10179c3a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hero_stats",
        sa.Column(
            "rank_filter",
            sa.String(),
            nullable=False,
            server_default="Mythic",
        ),
    )

    op.create_index(
        "ix_hero_stats_rank_filter",
        "hero_stats",
        ["rank_filter"],
    )


def downgrade() -> None:
    op.drop_index("ix_hero_stats_rank_filter", table_name="hero_stats")
    op.drop_column("hero_stats", "rank_filter")