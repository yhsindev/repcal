"""phase 1 init: users, identities, profiles, body_metrics, nutrition_phases

Revision ID: 0001
Revises:
Create Date: 2026-05-15

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("timezone", sa.Text(), nullable=False, server_default="Asia/Taipei"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "user_identities",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("platform", sa.Text(), nullable=False),
        sa.Column("external_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("platform", "external_id", name="uq_platform_external_id"),
    )
    op.create_index("ix_user_identities_user_id", "user_identities", ["user_id"])

    op.create_table(
        "user_profiles",
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("gender", sa.Text(), nullable=True),
        sa.Column("height_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("activity_level", sa.Text(), nullable=True),
        sa.Column("goal", sa.Text(), nullable=True),
        sa.Column("target_weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("tdee_override", sa.Integer(), nullable=True),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "body_metrics",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("recorded_on", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("body_fat_pct", sa.Numeric(4, 2), nullable=True),
        sa.Column("waist_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("chest_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("arm_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("thigh_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("user_id", "recorded_on", name="uq_body_metrics_user_date"),
    )
    op.create_index("ix_body_metrics_user_id", "body_metrics", ["user_id"])

    op.create_table(
        "nutrition_phases",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("phase_type", sa.Text(), nullable=False),  # cut / maintain / bulk
        sa.Column("started_on", sa.Date(), nullable=False),
        sa.Column("ended_on", sa.Date(), nullable=True),
        sa.Column("daily_kcal", sa.Integer(), nullable=False),
        sa.Column("daily_protein_g", sa.Integer(), nullable=False),
        sa.Column("daily_fat_g", sa.Integer(), nullable=False),
        sa.Column("daily_carb_g", sa.Integer(), nullable=False),
        sa.Column(
            "target_weight_change_kg_per_week",
            sa.Numeric(3, 2),
            nullable=True,
        ),
        sa.Column("estimated_tdee", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_nutrition_phases_user_id", "nutrition_phases", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_nutrition_phases_user_id", table_name="nutrition_phases")
    op.drop_table("nutrition_phases")
    op.drop_index("ix_body_metrics_user_id", table_name="body_metrics")
    op.drop_table("body_metrics")
    op.drop_table("user_profiles")
    op.drop_index("ix_user_identities_user_id", table_name="user_identities")
    op.drop_table("user_identities")
    op.drop_table("users")
