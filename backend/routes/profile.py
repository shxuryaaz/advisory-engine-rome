from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from models.schemas import BehavioralPattern, Goal, UserConstraints
from services.database import database

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/goals", response_model=Goal)
async def upsert_goal(goal: Goal) -> Goal:
    row = await database.fetchrow(
        """
        INSERT INTO goals (id, user_id, title, description, weight)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            weight = EXCLUDED.weight
        RETURNING id, user_id, title, description, weight
        """,
        goal.id,
        goal.user_id,
        goal.title,
        goal.description,
        goal.weight,
    )
    assert row is not None
    return Goal.model_validate(dict(row))


@router.put("/constraints/{user_id}", response_model=UserConstraints)
async def upsert_constraints(user_id: UUID, constraints: UserConstraints) -> UserConstraints:
    row = await database.fetchrow(
        """
        INSERT INTO user_constraints (user_id, time_per_day, budget, energy_level)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (user_id) DO UPDATE SET
            time_per_day = EXCLUDED.time_per_day,
            budget = EXCLUDED.budget,
            energy_level = EXCLUDED.energy_level,
            updated_at = now()
        RETURNING user_id, time_per_day, budget, energy_level
        """,
        user_id,
        constraints.time_per_day,
        constraints.budget,
        constraints.energy_level,
    )
    assert row is not None
    return UserConstraints.model_validate(dict(row))


@router.get("/patterns/{user_id}", response_model=list[BehavioralPattern])
async def get_patterns(user_id: UUID) -> list[BehavioralPattern]:
    rows = await database.fetch(
        """
        SELECT id, user_id, pattern, confidence_score
        FROM behavioral_patterns
        WHERE user_id = $1
        ORDER BY confidence_score DESC, updated_at DESC
        """,
        user_id,
    )
    return [BehavioralPattern.model_validate(dict(row)) for row in rows]
