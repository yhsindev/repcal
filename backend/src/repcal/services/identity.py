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
    # Two-step lookup avoids `.join()` whose on-clause type confuses mypy
    # without the SQLAlchemy mypy plugin. Two queries here is trivial cost.
    identity_result = await session.execute(
        select(UserIdentity).where(
            UserIdentity.platform == platform.value,
            UserIdentity.external_id == external_id,
        )
    )
    identity = identity_result.scalar_one_or_none()

    if identity is not None:
        user = await session.get(User, identity.user_id)
        assert user is not None, "user_id in identity should always reference a user"
        return user

    user = User(display_name=display_name)
    session.add(user)
    await session.flush()  # populate user.id

    assert user.id is not None
    new_identity = UserIdentity(
        user_id=user.id,
        platform=platform.value,
        external_id=external_id,
    )
    session.add(new_identity)
    await session.flush()
    return user
