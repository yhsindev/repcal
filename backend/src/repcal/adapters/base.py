"""Abstract messaging adapter.

This Protocol is the seam between the bot's user-facing layer and business
logic. To add a new platform (e.g. LINE), implement this Protocol — services
don't need to change.

Kept deliberately minimal: only adds methods when we actually need them.
YAGNI > premature abstraction.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class Platform(StrEnum):
    DISCORD = "discord"
    LINE = "line"
    TELEGRAM = "telegram"


@dataclass(frozen=True, slots=True)
class IncomingMessage:
    """A normalized message from any messaging platform.

    Adapters translate platform-specific events into this shape before
    handing off to services / handlers.
    """

    platform: Platform
    external_user_id: str
    text: str
    # image_urls: list[str]  # add when we tackle photo logging (Phase 2)


class MessagingAdapter(Protocol):
    """Operations a messaging platform must support.

    Add a method only when a service actually needs it. Right now we don't
    need to send images or open modals from services — slash commands handle
    replies directly via their own platform API. This Protocol exists mainly
    to document the boundary; it will grow when conversational flows replace
    structured commands in Phase 2.
    """

    platform: Platform

    async def send_text(self, external_user_id: str, text: str) -> None:
        """Send a plain text message to the user (e.g. weekly digest push)."""
        ...
