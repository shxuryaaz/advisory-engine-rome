from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


AgentKind = Literal["strategist", "operator", "critic", "risk_manager"]


class User(BaseModel):
    id: UUID
    name: str


class Goal(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str
    weight: float = Field(ge=0, le=1)


class UserConstraints(BaseModel):
    user_id: UUID
    time_per_day: float | None = Field(default=None, ge=0)
    budget: float | None = Field(default=None, ge=0)
    energy_level: float | None = Field(default=None, ge=0, le=1)


class BehavioralPattern(BaseModel):
    id: UUID
    user_id: UUID
    pattern: str
    confidence_score: float = Field(ge=0, le=1)


class DecisionOption(BaseModel):
    id: str
    label: str
    description: str = ""
    estimated_time: float | None = Field(default=None, ge=0)
    estimated_cost: float | None = Field(default=None, ge=0)
    expected_value: float | None = Field(default=None, ge=0, le=1)


class DecisionRequest(BaseModel):
    user_id: UUID
    decision: str = Field(min_length=3)
    options: list[DecisionOption] = Field(min_length=1)


class AgentResult(BaseModel):
    agent: AgentKind
    score: float = Field(ge=0, le=1)
    reasoning: str
    warnings: list[str] = Field(default_factory=list)


class DecisionResponse(BaseModel):
    decision_id: UUID
    version: int
    recommended_option: str
    score: float = Field(ge=0, le=1)
    agent_breakdown: dict[str, AgentResult]
    reasoning: str
    alternatives: list[dict[str, Any]]


class StoredDecision(BaseModel):
    id: UUID
    user_id: UUID
    decision_text: str
    options: list[dict[str, Any]]
    chosen_option: str
    reasoning: str
    version: int
    final_score: float
    agent_breakdown: dict[str, Any]
    created_at: datetime


class FeedbackRequest(BaseModel):
    decision_id: UUID
    outcome_summary: str = Field(min_length=3)
    success_score: float = Field(ge=0, le=1)
    reflection: str = ""


class FeedbackResponse(BaseModel):
    outcome_id: UUID
    updated_patterns: list[BehavioralPattern]


class MemoryQuery(BaseModel):
    user_id: UUID
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class MemoryItem(BaseModel):
    id: UUID
    user_id: UUID
    content: str
    source_type: str
    source_id: UUID | None = None
    similarity: float | None = None
    created_at: datetime


class UserContext(BaseModel):
    user: User
    goals: list[Goal]
    constraints: UserConstraints | None
    behavioral_patterns: list[BehavioralPattern]
    recent_decisions: list[dict[str, Any]]
    relevant_memory: list[MemoryItem]
