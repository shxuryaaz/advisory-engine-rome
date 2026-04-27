from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from models.schemas import (
    BehavioralPattern,
    FeedbackRequest,
    FeedbackResponse,
    Goal,
    MemoryItem,
    User,
    UserConstraints,
    UserContext,
)
from memory.semantic import semantic_memory
from services.database import database


def _json(value: Any) -> Any:
    if isinstance(value, str):
        return json.loads(value)
    return value


class UserModelService:
    async def get_or_create_user(self, user_id: UUID, name: str = "Default User") -> User:
        row = await database.fetchrow(
            """
            INSERT INTO users (id, name)
            VALUES ($1, $2)
            ON CONFLICT (id) DO UPDATE SET name = users.name
            RETURNING id, name
            """,
            user_id,
            name,
        )
        assert row is not None
        return User(id=row["id"], name=row["name"])

    async def build_context(
        self,
        *,
        user_id: UUID,
        query: str,
        top_k: int = 5,
    ) -> UserContext:
        user = await self.get_or_create_user(user_id)
        relevant_memory = await semantic_memory.retrieve_relevant_memory(user_id=user_id, query=query, top_k=top_k)
        goals = [
            Goal.model_validate(dict(row))
            for row in await database.fetch(
                "SELECT id, user_id, title, description, weight FROM goals WHERE user_id = $1 ORDER BY weight DESC",
                user_id,
            )
        ]
        constraints_row = await database.fetchrow(
            "SELECT user_id, time_per_day, budget, energy_level FROM constraints WHERE user_id = $1",
            user_id,
        )
        patterns = [
            BehavioralPattern.model_validate(dict(row))
            for row in await database.fetch(
                """
                SELECT id, user_id, pattern, confidence_score
                FROM behavioral_patterns
                WHERE user_id = $1
                ORDER BY confidence_score DESC, updated_at DESC
                LIMIT 20
                """,
                user_id,
            )
        ]
        recent_decisions = [
            {
                "id": row["id"],
                "decision_text": row["decision_text"],
                "options": _json(row["options"]),
                "chosen_option": row["chosen_option"],
                "reasoning": row["reasoning"],
                "timestamp": row["timestamp"],
                "version": row["version"],
            }
            for row in await database.fetch(
                """
                SELECT id, decision_text, options, chosen_option, reasoning, timestamp, version
                FROM decision_history
                WHERE user_id = $1
                ORDER BY timestamp DESC
                LIMIT 10
                """,
                user_id,
            )
        ]

        return UserContext(
            user=user,
            goals=goals,
            constraints=UserConstraints.model_validate(dict(constraints_row)) if constraints_row else None,
            behavioral_patterns=patterns,
            recent_decisions=recent_decisions,
            relevant_memory=relevant_memory,
        )

    async def update_user_model(self, feedback: FeedbackRequest) -> FeedbackResponse:
        decision_row = await database.fetchrow(
            "SELECT id, user_id, decision_text, chosen_option, reasoning FROM decision_history WHERE id = $1",
            feedback.decision_id,
        )
        if decision_row is None:
            raise ValueError("Decision not found")

        outcome_row = await database.fetchrow(
            """
            INSERT INTO outcomes (decision_id, outcome_summary, success_score, reflection)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            feedback.decision_id,
            feedback.outcome_summary,
            feedback.success_score,
            feedback.reflection,
        )
        assert outcome_row is not None

        pattern_text = self._derive_pattern_text(dict(decision_row), feedback)
        confidence = self._derive_confidence(feedback.success_score)
        pattern_row = await database.fetchrow(
            """
            INSERT INTO behavioral_patterns (user_id, pattern, confidence_score)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, pattern)
            DO UPDATE SET
                confidence_score = LEAST(1.0, (behavioral_patterns.confidence_score + EXCLUDED.confidence_score) / 2 + 0.1),
                updated_at = now()
            RETURNING id, user_id, pattern, confidence_score
            """,
            decision_row["user_id"],
            pattern_text,
            confidence,
        )
        assert pattern_row is not None

        await semantic_memory.store_memory(
            user_id=decision_row["user_id"],
            text=(
                f"Outcome for decision '{decision_row['decision_text']}': {feedback.outcome_summary}. "
                f"Success score: {feedback.success_score}. Reflection: {feedback.reflection}"
            ),
            source_type="outcome",
            source_id=outcome_row["id"],
        )
        await semantic_memory.store_memory(
            user_id=decision_row["user_id"],
            text=f"Behavioral pattern learned: {pattern_text}",
            source_type="pattern",
            source_id=pattern_row["id"],
        )

        return FeedbackResponse(
            outcome_id=outcome_row["id"],
            updated_patterns=[BehavioralPattern.model_validate(dict(pattern_row))],
        )

    @staticmethod
    def _derive_pattern_text(decision: dict[str, Any], feedback: FeedbackRequest) -> str:
        if feedback.success_score >= 0.7:
            return (
                f"Decisions like '{decision['decision_text']}' work better when the user follows reasoning: "
                f"{decision['reasoning'][:220]}"
            )
        return (
            f"Decision type '{decision['decision_text']}' has underperformed; inspect assumptions around "
            f"chosen option '{decision['chosen_option']}' and reflection '{feedback.reflection[:220]}'."
        )

    @staticmethod
    def _derive_confidence(success_score: float) -> float:
        distance_from_neutral = abs(success_score - 0.5)
        return min(1.0, 0.45 + distance_from_neutral)


user_model_service = UserModelService()
