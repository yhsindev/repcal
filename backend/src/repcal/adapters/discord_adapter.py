"""Discord implementation of MessagingAdapter."""

from __future__ import annotations

import logging

import discord

from repcal.adapters.base import Platform

logger = logging.getLogger(__name__)


class DiscordAdapter:
    """Wraps a `discord.Client` to satisfy the `MessagingAdapter` Protocol.

    Most of the bot's UX lives in slash commands (which reply via the
    `Interaction` object directly) — this adapter is for *unsolicited*
    messages, e.g. pushing a weekly digest to a user we haven't been
    talking to.
    """

    platform: Platform = Platform.DISCORD

    def __init__(self, client: discord.Client) -> None:
        self._client = client

    async def send_text(self, external_user_id: str, text: str) -> None:
        try:
            user = await self._client.fetch_user(int(external_user_id))
        except (discord.NotFound, ValueError) as e:
            logger.warning("discord user not found: %s (%s)", external_user_id, e)
            return

        try:
            await user.send(text)
        except discord.Forbidden:
            logger.warning(
                "cannot DM discord user %s — they may have DMs closed",
                external_user_id,
            )
