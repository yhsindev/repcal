"""User, identity, and profile models."""

from __future__ import annotations

from datetime import date, datetime
from datetime import timezone as _tz

from sqlmodel import Field, SQLModel, UniqueConstraint


def _utcnow() -> datetime:
    return datetime.now(_tz.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    display_name: str | None = Field(default=None)
    timezone: str = Field(default="Asia/Taipei")
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class UserIdentity(SQLModel, table=True):
    """Maps an external platform user (Discord/LINE/...) to an internal User."""

    __tablename__ = "user_identities"
    __table_args__ = (
        UniqueConstraint("platform", "external_id", name="uq_platform_external_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    platform: str = Field(description="discord / line / telegram")
    external_id: str = Field(description="platform-specific user id")
    created_at: datetime = Field(default_factory=_utcnow)


class UserProfile(SQLModel, table=True):
    """Static (or slow-changing) physical attributes. Daily nutrition targets live in
    `nutrition_phases`, not here — single source of truth.
    """

    __tablename__ = "user_profiles"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    birth_date: date | None = Field(default=None)
    gender: str | None = Field(default=None)
    height_cm: float | None = Field(default=None)
    activity_level: str | None = Field(
        default=None,
        description="sedentary / light / moderate / active / very_active",
    )
    goal: str | None = Field(default=None, description="cut / maintain / bulk")
    target_weight_kg: float | None = Field(default=None)
    tdee_override: int | None = Field(
        default=None,
        description="Manually overridden TDEE; usually derived from active phase",
    )
    updated_at: datetime = Field(default_factory=_utcnow)
