"""Body metric service: weight, body fat, circumferences."""

from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from repcal.models.body import BodyMetric


async def record_weight(
    session: AsyncSession,
    user_id: int,
    weight_kg: float,
    recorded_on: date | None = None,
) -> BodyMetric:
    """Record (or overwrite) today's weight for a user.

    Following the `(user_id, recorded_on)` unique constraint, repeated calls
    on the same day update the existing row rather than creating a duplicate.
    """
    if recorded_on is None:
        recorded_on = date.today()

    result = await session.execute(
        select(BodyMetric).where(
            BodyMetric.user_id == user_id,
            BodyMetric.recorded_on == recorded_on,
        )
    )
    existing = result.scalar_one_or_none()

    if existing is not None:
        existing.weight_kg = weight_kg
        session.add(existing)
        await session.flush()
        return existing

    metric = BodyMetric(
        user_id=user_id,
        recorded_on=recorded_on,
        weight_kg=weight_kg,
    )
    session.add(metric)
    await session.flush()
    return metric
