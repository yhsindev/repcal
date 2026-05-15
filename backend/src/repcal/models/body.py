"""Body metrics: weight, body fat, circumferences, progress photo."""

from __future__ import annotations

from datetime import date, datetime
from datetime import timezone as _tz

from sqlmodel import Field, SQLModel, UniqueConstraint


def _utcnow() -> datetime:
    return datetime.now(_tz.utc)


class BodyMetric(SQLModel, table=True):
    """One row per day per user (last write wins via upsert)."""

    __tablename__ = "body_metrics"
    __table_args__ = (
        UniqueConstraint("user_id", "recorded_on", name="uq_body_metrics_user_date"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    recorded_on: date = Field(description="The date this measurement is for")

    weight_kg: float | None = Field(default=None)
    body_fat_pct: float | None = Field(default=None)
    waist_cm: float | None = Field(default=None)
    chest_cm: float | None = Field(default=None)
    arm_cm: float | None = Field(default=None)
    thigh_cm: float | None = Field(default=None)

    photo_url: str | None = Field(default=None)
    notes: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=_utcnow)
