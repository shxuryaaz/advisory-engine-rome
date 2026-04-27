from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from config import settings
from services.user_model import user_model_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def dashboard(user_id: UUID | None = None) -> dict:
    target_user = user_id or UUID(settings.default_user_id)
    context = await user_model_service.build_context(
        user_id=target_user,
        query="recent decisions and behavioral patterns",
    )
    return {
        "user": context.user.model_dump(mode="json"),
        "goals": [goal.model_dump(mode="json") for goal in context.goals],
        "constraints": context.constraints.model_dump(mode="json") if context.constraints else None,
        "patterns": [pattern.model_dump(mode="json") for pattern in context.behavioral_patterns],
        "recent_decisions": context.recent_decisions,
    }
