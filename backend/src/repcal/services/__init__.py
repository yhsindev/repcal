"""Business logic services.

Services depend only on:
- SQLAlchemy AsyncSession (for persistence)
- Pure Python types

They do NOT depend on Discord, FastAPI, or any messaging platform.
This is what makes the adapter pattern useful: services are reusable
across any input channel.
"""
