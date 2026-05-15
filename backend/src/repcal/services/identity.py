"""Identity service.

Maps an external (platform, user_id) pair to an internal `User` row,
creating the user on first contact.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from repcal.adapters.base import Platform
from repcal.models.user import User, UserIdentity


async def get_or_create_user(
    session: AsyncSession,
    platform: Platform,
    external_id: str,
    display_name: str | None = None,
) -> User:
    """Find the User behind an external identity, creating one if needed.

    Idempotent: safe to call on every incoming message.
    """
    result = await session.execute(
        select(User)
        .join(UserIdentity, UserIdentity.user_id == User.id)
        .where(
            UserIdentity.platform == platform.value,
            UserIdentity.external_id == external_id,
        )
    )
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    user = User(display_name=display_name)
    session.add(user)
    await session.flush()  # populate user.id

    assert user.id is not None
    identity = UserIdentity(
        user_id=user.id,
        platform=platform.value,
        external_id=external_id,
    )
    session.add(identity)
    await session.flush()
    return user
