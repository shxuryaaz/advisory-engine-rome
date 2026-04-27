from __future__ import annotations

from agents.base import DecisionAgent, clamp_score, weighted_goal_signal
from models.schemas import DecisionOption, UserContext


class StrategistAgent(DecisionAgent):
    name = "strategist"
    system_focus = "Evaluate long-term alignment with weighted user goals and trajectory."

    def fallback_score(self, option: DecisionOption, context: UserContext) -> float:
        return weighted_goal_signal(context, option)


class OperatorAgent(DecisionAgent):
    name = "operator"
    system_focus = "Evaluate execution feasibility using time, budget, and energy constraints."

    def fallback_score(self, option: DecisionOption, context: UserContext) -> float:
        score = 0.72
        constraints = context.constraints
        if constraints:
            if option.estimated_time and constraints.time_per_day:
                score -= max(0.0, option.estimated_time - constraints.time_per_day) * 0.12
            if option.estimated_cost and constraints.budget:
                over_budget_ratio = max(0.0, option.estimated_cost - constraints.budget) / max(constraints.budget, 1.0)
                score -= min(0.35, over_budget_ratio * 0.35)
            if constraints.energy_level is not None and constraints.energy_level < 0.4:
                score -= 0.15
        return clamp_score(score)


class CriticAgent(DecisionAgent):
    name = "critic"
    system_focus = "Detect behavioral flaws, repeated failure modes, bias, and self-sabotage."

    def fallback_score(self, option: DecisionOption, context: UserContext) -> float:
        option_text = f"{option.label} {option.description}".lower()
        penalty = 0.0
        for pattern in context.behavioral_patterns:
            pattern_terms = {term for term in pattern.pattern.lower().split() if len(term) > 4}
            if any(term in option_text for term in pattern_terms):
                penalty += 0.2 * pattern.confidence_score
        return clamp_score(0.78 - penalty)


class RiskManagerAgent(DecisionAgent):
    name = "risk_manager"
    system_focus = "Enforce constraints and flag dangerous downside or irreversible risk."

    def fallback_score(self, option: DecisionOption, context: UserContext) -> float:
        score = 0.82
        constraints = context.constraints
        if constraints and option.estimated_cost and constraints.budget:
            if option.estimated_cost > constraints.budget:
                score -= 0.35
        risky_terms = ("debt", "quit", "all-in", "irreversible", "unsafe", "illegal")
        option_text = f"{option.label} {option.description}".lower()
        if any(term in option_text for term in risky_terms):
            score -= 0.25
        return clamp_score(score)


def build_default_agents() -> list[DecisionAgent]:
    return [StrategistAgent(), OperatorAgent(), CriticAgent(), RiskManagerAgent()]


AGENTS = build_default_agents()
