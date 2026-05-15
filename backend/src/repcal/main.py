"""Application entrypoint.

Phase 1: starts the Discord bot only.
Later phases will add FastAPI (for LIFF/PWA HTTP endpoints) running concurrently
in the same asyncio event loop.
"""

from __future__ import annotations

import asyncio
import logging

from repcal.bot.client import create_bot
from repcal.config import settings


def _setup_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


async def main_async() -> None:
    _setup_logging()
    bot = create_bot()
    await bot.start(settings.discord_bot_token)


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
