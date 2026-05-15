"""Unit tests for body metric service."""

from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from repcal.adapters.base import Platform
from repcal.services import body as body_service
from repcal.services import identity as identity_service


async def test_record_weight_creates_row(session: AsyncSession) -> None:
    user = await identity_service.get_or_create_user(
        session, Platform.DISCORD, "discord-user-123"
    )
    assert user.id is not None

    metric = await body_service.record_weight(
        session,
        user_id=user.id,
        weight_kg=72.5,
        recorded_on=date(2026, 5, 15),
    )
    assert metric.weight_kg == 72.5
    assert metric.recorded_on == date(2026, 5, 15)
    assert metric.user_id == user.id


async def test_record_weight_same_day_overwrites(session: AsyncSession) -> None:
    """Two records on the same day should result in one row, not two."""
    user = await identity_service.get_or_create_user(
        session, Platform.DISCORD, "discord-user-456"
    )
    assert user.id is not None

    today = date(2026, 5, 15)
    first = await body_service.record_weight(
        session, user_id=user.id, weight_kg=72.5, recorded_on=today
    )
    second = await body_service.record_weight(
        session, user_id=user.id, weight_kg=72.3, recorded_on=today
    )

    assert first.id == second.id
    assert second.weight_kg == 72.3


async def test_get_or_create_user_is_idempotent(session: AsyncSession) -> None:
    """Repeated calls with the same identity return the same User row."""
    u1 = await identity_service.get_or_create_user(session, Platform.DISCORD, "abc")
    u2 = await identity_service.get_or_create_user(session, Platform.DISCORD, "abc")
    assert u1.id == u2.id


async def test_different_platforms_get_different_users(session: AsyncSession) -> None:
    """Same external_id on different platforms = different users (correct,
    since '12345' as a Discord ID has nothing to do with '12345' as a LINE ID)."""
    discord_user = await identity_service.get_or_create_user(
        session, Platform.DISCORD, "12345"
    )
    line_user = await identity_service.get_or_create_user(session, Platform.LINE, "12345")
    assert discord_user.id != line_user.id
