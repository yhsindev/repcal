"""`/weight` slash command — record today's body weight."""

from __future__ import annotations

import logging

import discord
from discord import app_commands

from repcal.adapters.base import Platform
from repcal.db import get_session
from repcal.services import body as body_service
from repcal.services import identity as identity_service

logger = logging.getLogger(__name__)


def register_weight_command(tree: app_commands.CommandTree) -> None:
    @tree.command(name="weight", description="紀錄今日體重 (kg)")
    @app_commands.describe(value="體重 (kg)，例如 72.5")
    async def weight(interaction: discord.Interaction, value: float) -> None:
        if value <= 0 or value > 500:
            await interaction.response.send_message(
                f"⚠️ 體重 {value}kg 看起來不太對，請確認再輸入。",
                ephemeral=True,
            )
            return

        # `defer` because DB round-trip may exceed Discord's 3s interaction limit
        # on cold connections.
        await interaction.response.defer(ephemeral=True)

        try:
            async with get_session() as session:
                user = await identity_service.get_or_create_user(
                    session,
                    platform=Platform.DISCORD,
                    external_id=str(interaction.user.id),
                    display_name=interaction.user.display_name,
                )
                assert user.id is not None
                metric = await body_service.record_weight(
                    session,
                    user_id=user.id,
                    weight_kg=value,
                )
        except Exception:
            logger.exception("failed to record weight for user %s", interaction.user.id)
            await interaction.followup.send(
                "❌ 寫入失敗，稍後再試。", ephemeral=True
            )
            return

        await interaction.followup.send(
            f"✓ 已紀錄 {metric.weight_kg}kg（{metric.recorded_on.isoformat()}）",
            ephemeral=True,
        )
