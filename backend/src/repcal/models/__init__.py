"""SQLModel table definitions.

Importing this module registers all tables with `SQLModel.metadata`.
Alembic's `env.py` imports `metadata` from here.
"""

from __future__ import annotations

from sqlmodel import SQLModel

from repcal.models.body import BodyMetric
from repcal.models.nutrition import NutritionPhase
from repcal.models.user import User, UserIdentity, UserProfile

metadata = SQLModel.metadata

__all__ = [
    "BodyMetric",
    "NutritionPhase",
    "User",
    "UserIdentity",
    "UserProfile",
    "metadata",
]
