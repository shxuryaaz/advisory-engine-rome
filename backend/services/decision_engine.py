from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from agents.implementations import AGENTS
from memory.semantic import semantic_memory
from models.schemas import AgentResult, DecisionRequest, DecisionResponse
from services.database import database
from services.user_model import user_model_service

logger = logging.getLogger(__name__)


class DecisionEngine:
    async def decide(self, request: DecisionRequest) -> DecisionResponse:
        relevant_memory = await semantic_memory.retrieve_relevant_memory(
            user_id=request.user_id,
            query=request.decision,
            top_k=5,
        )
        context = await user_model_service.build_context(
            user_id=request.user_id,
            relevant_memory=relevant_memory,
        )
        option_evaluations = await asyncio.gather(
            *[
                self._evaluate_option(request.decision, option, context)
                for option in request.options
            ]
        )
        ranked = sorted(option_evaluations, key=lambda item: item["score"], reverse=True)
        winner = ranked[0]

        decision_id, version = await self._persist_decision(
            request=request,
            recommended_option=winner["option_id"],
            reasoning=winner["reasoning"],
            score=winner["score"],
            agent_breakdown=winner["agent_breakdown"],
        )
        await semantic_memory.store_memory(
            user_id=request.user_id,
            text=f"Decision: {request.decision}. Recommended: {winner['option_label']}. Reasoning: {winner['reasoning']}",
            source_type="decision",
            source_id=decision_id,
        )

        logger.info(
            "decision_completed",
            extra={
                "decision_id": str(decision_id),
                "user_id": str(request.user_id),
                "recommended_option": winner["option_id"],
                "score": winner["score"],
                "version": version,
            },
        )

        return DecisionResponse(
            decision_id=decision_id,
            version=version,
            recommended_option=winner["option_id"],
            score=winner["score"],
            agent_breakdown=winner["agent_breakdown"],
            reasoning=winner["reasoning"],
            alternatives=[
                {
                    "option_id": item["option_id"],
                    "label": item["option_label"],
                    "score": item["score"],
                    "reasoning": item["reasoning"],
                }
                for item in ranked[1:]
            ],
        )

    async def _evaluate_option(self, decision: str, option, context, options) -> dict:
        agent_results = await asyncio.gather(
            *[
                agent.evaluate(decision=decision, option=option, options=options, context=context)
                for agent in AGENTS
            ]
        )
        breakdown: dict[str, AgentResult] = {result.agent: result for result in agent_results}
        score = self._aggregate_score(breakdown)
        reasoning = self._summarize(option.label, breakdown, score)
        return {
            "option_id": option.id,
            "option_label": option.label,
            "score": score,
            "agent_breakdown": breakdown,
            "reasoning": reasoning,
        }

    @staticmethod
    def _aggregate_score(breakdown: dict[str, AgentResult]) -> float:
        strategist = breakdown["strategist"].score
        operator = breakdown["operator"].score
        critic_penalty = 1.0 - breakdown["critic"].score
        risk_penalty = 1.0 - breakdown["risk_manager"].score
        final = (strategist * 0.4) + (operator * 0.3) + (critic_penalty * -0.2) + (risk_penalty * -0.1)
        return round(min(1.0, max(0.0, final)), 4)

    @staticmethod
    def _summarize(option_label: str, breakdown: dict[str, AgentResult], score: float) -> str:
        strongest = max(breakdown.values(), key=lambda result: result.score)
        weakest = min(breakdown.values(), key=lambda result: result.score)
        return (
            f"{option_label} scored {score:.2f}. Strongest signal: {strongest.agent} "
            f"({strongest.score:.2f}) - {strongest.reasoning} Weakest signal: {weakest.agent} "
            f"({weakest.score:.2f}) - {weakest.reasoning}"
        )

    async def _persist_decision(
        self,
        *,
        request: DecisionRequest,
        recommended_option: str,
        reasoning: str,
        score: float,
        agent_breakdown: dict[str, AgentResult],
    ) -> tuple[UUID, int]:
        row = await database.fetchrow(
            """
            INSERT INTO decision_history (
                user_id, decision_text, options, chosen_option, reasoning, final_score, agent_breakdown, version
            )
            VALUES ($1, $2, $3::jsonb, $4, $5, $6, $7::jsonb,
                COALESCE((
                    SELECT MAX(version) + 1
                    FROM decision_history
                    WHERE user_id = $1 AND decision_text = $2
                ), 1)
            )
            RETURNING id, version
            """,
            request.user_id,
            request.decision,
            [option.model_dump(mode="json") for option in request.options],
            recommended_option,
            reasoning,
            score,
            {agent: result.model_dump(mode="json") for agent, result in agent_breakdown.items()},
        )
        assert row is not None
        return row["id"], row["version"]


decision_engine = DecisionEngine()
