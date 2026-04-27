from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from agents.prompts import AGENT_SYSTEM_PROMPTS, render_agent_prompt
from models.schemas import AgentResult, DecisionOption, UserContext
from services.openai_client import OpenAIService

logger = logging.getLogger(__name__)


class DecisionAgent(ABC):
    """OpenAI-backed evaluator for a specific decision lens."""

    name: str
    system_focus: str

    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai = openai_service or OpenAIService()

    @abstractmethod
    def fallback_score(self, option: DecisionOption, context: UserContext) -> float:
        """Deterministic fallback used when the OpenAI API is unavailable."""

    async def evaluate(
        self,
        *,
        decision: str,
        option: DecisionOption,
        options: list[DecisionOption],
        context: UserContext,
    ) -> AgentResult:
        prompt = render_agent_prompt(
            agent=self.name,  # type: ignore[arg-type]
            context=context,
            decision=decision,
            options=options,
        )

        try:
            payload = await self.openai.complete_json(
                system_prompt=AGENT_SYSTEM_PROMPTS[self.name],  # type: ignore[index]
                user_payload={
                    "agent": self.name,
                    "decision": decision,
                    "option_under_review": option.model_dump(),
                    "full_prompt": prompt,
                },
            )
            return self._coerce_result(payload)
        except Exception as exc:  # pragma: no cover - exercised when API credentials are absent
            logger.warning("agent_fallback", extra={"agent": self.name, "error": str(exc)})
            score = self.fallback_score(option, context)
            return AgentResult(
                agent=self.name,  # type: ignore[arg-type]
                score=score,
                reasoning=(
                    f"Fallback {self.name} evaluation used because model execution was unavailable. "
                    f"The score reflects available structured profile data and option metadata."
                ),
                warnings=["AI model unavailable; deterministic fallback used."],
            )

    def _coerce_result(self, payload: dict[str, Any]) -> AgentResult:
        payload["agent"] = self.name
        payload["score"] = min(1.0, max(0.0, float(payload.get("score", 0.0))))
        if isinstance(payload.get("warnings"), str):
            payload["warnings"] = [payload["warnings"]]
        return AgentResult.model_validate(payload)


def clamp_score(value: float) -> float:
    return min(1.0, max(0.0, value))


def weighted_goal_signal(context: UserContext, option: DecisionOption) -> float:
    if not context.goals:
        return option.expected_value if option.expected_value is not None else 0.55

    option_text = f"{option.label} {option.description}".lower()
    matched_weight = 0.0
    total_weight = sum(goal.weight for goal in context.goals) or 1.0
    for goal in context.goals:
        goal_terms = set(f"{goal.title} {goal.description}".lower().split())
        if any(term in option_text for term in goal_terms if len(term) > 3):
            matched_weight += goal.weight
    base = matched_weight / total_weight
    expected = option.expected_value if option.expected_value is not None else 0.55
    return clamp_score((base * 0.65) + (expected * 0.35))


def compact_json(data: Any) -> str:
    return json.dumps(data, default=str, separators=(",", ":"))
