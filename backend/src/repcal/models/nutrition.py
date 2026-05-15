"""Nutrition phase: cut / maintain / bulk periods with associated macro targets."""

from __future__ import annotations

from datetime import date, datetime
from datetime import timezone as _tz

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(_tz.utc)


class NutritionPhase(SQLModel, table=True):
    """A nutrition phase (cut / maintain / bulk) defines the daily targets that
    apply during a date range. Only one phase per user should be "active"
    (ended_on is null) at any time, but this is enforced in application logic,
    not the DB.
    """

    __tablename__ = "nutrition_phases"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str | None = Field(default=None)
    phase_type: str = Field(description="cut / maintain / bulk")

    started_on: date = Field()
    ended_on: date | None = Field(
        default=None,
        description="null = currently active",
    )

    daily_kcal: int = Field()
    daily_protein_g: int = Field()
    daily_fat_g: int = Field()
    daily_carb_g: int = Field()

    target_weight_change_kg_per_week: float | None = Field(
        default=None,
        description="negative for cut, positive for bulk, zero for maintain",
    )
    estimated_tdee: int | None = Field(
        default=None,
        description="Back-calculated from actual intake & weight change",
    )

    created_at: datetime = Field(default_factory=_utcnow)
