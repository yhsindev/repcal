"""Messaging platform adapters.

The `MessagingAdapter` Protocol decouples business logic from any specific
chat platform (Discord, LINE, Telegram, ...). Services depend on this
Protocol, not on a concrete adapter.
"""

from repcal.adapters.base import IncomingMessage, MessagingAdapter, Platform

__all__ = ["IncomingMessage", "MessagingAdapter", "Platform"]
