"""Discord bot client factory.

Sets up intents, the command tree, and slash command registration.
"""

from __future__ import annotations

import logging

import discord
from discord import app_commands

from repcal.bot.commands.weight import register_weight_command
from repcal.config import settings

logger = logging.getLogger(__name__)


class RepcalBot(discord.Client):
    """Custom Client subclass so we can hook `setup_hook` for command syncing."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        # Required to read message content if we ever use prefix commands /
        # raw message events. Slash commands work without it, but we'll
        # need it for Phase 2 (parsing free-text food logs).
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        # Register slash commands defined in repcal.bot.commands.*
        register_weight_command(self.tree)

        # Sync to a specific guild for instant availability during dev.
        # Without a guild ID, global sync takes up to ~1 hour to propagate.
        if settings.discord_guild_id is not None:
            guild = discord.Object(id=settings.discord_guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(
                "synced %d slash command(s) to guild %s",
                len(synced),
                settings.discord_guild_id,
            )
        else:
            synced = await self.tree.sync()
            logger.info(
                "synced %d global slash command(s) — may take up to 1h to appear",
                len(synced),
            )

    async def on_ready(self) -> None:
        assert self.user is not None
        logger.info("logged in as %s (id=%s)", self.user, self.user.id)


def create_bot() -> RepcalBot:
    return RepcalBot()
