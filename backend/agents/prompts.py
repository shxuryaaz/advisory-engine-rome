from __future__ import annotations

from models.schemas import AgentKind, DecisionOption, UserContext


AGENT_SYSTEM_PROMPTS: dict[AgentKind, str] = {
    "strategist": (
        "You are the Strategist Agent in a Personal Decision Intelligence System. "
        "Judge long-term alignment with weighted user goals and trajectory. Be direct, critical, and specific."
    ),
    "operator": (
        "You are the Operator Agent. Judge execution feasibility using time, budget, energy, and operational drag. "
        "Prefer practical truth over motivational advice."
    ),
    "critic": (
        "You are the Critic Agent. Identify behavioral flaws, repeated failure modes, cognitive biases, and self-sabotage. "
        "A high score means low behavioral risk; a low score means substantial risk."
    ),
    "risk_manager": (
        "You are the Risk Manager Agent. Enforce hard constraints and flag dangerous downside, overcommitment, "
        "financial risk, health risk, and irreversible choices. A high score means acceptable risk."
    ),
}


def render_agent_prompt(
    *,
    agent: AgentKind,
    context: UserContext,
    decision: str,
    options: list[DecisionOption],
) -> str:
    goals = [
        {"title": goal.title, "description": goal.description, "weight": goal.weight}
        for goal in context.goals
    ]
    patterns = [
        {"pattern": pattern.pattern, "confidence": pattern.confidence_score}
        for pattern in context.behavioral_patterns
    ]
    memories = [
        {
            "content": memory.content,
            "source_type": memory.source_type,
            "similarity": memory.similarity,
        }
        for memory in context.relevant_memory
    ]

    return f"""
Assess this decision for user {context.user.name}.

User goals with weights:
{goals}

Current constraints:
{context.constraints.model_dump() if context.constraints else {}}

Known behavioral flaws and patterns:
{patterns}

Relevant past decisions, reflections, and patterns:
{memories}

Current decision:
{decision}

Options:
{[option.model_dump() for option in options]}

Return only JSON matching this schema:
{{
  "agent": "{agent}",
  "score": 0.0,
  "reasoning": "direct, non-generic reasoning tied to this user",
  "warnings": ["specific warning"]
}}

Scoring guidance:
- 1.0 means strongly favorable for your agent's responsibility.
- 0.5 means mixed or uncertain.
- 0.0 means strongly unfavorable or dangerous.
""".strip()


def build_agent_prompt(
    *,
    agent_name: AgentKind,
    focus: str,
    context: UserContext,
    decision: str,
    option: DecisionOption,
) -> str:
    base_prompt = render_agent_prompt(
        agent=agent_name,
        context=context,
        decision=decision,
        options=[option],
    )
    return f"{AGENT_SYSTEM_PROMPTS[agent_name]}\n\nAgent focus:\n{focus}\n\n{base_prompt}"
