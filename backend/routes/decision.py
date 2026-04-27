from __future__ import annotations

from fastapi import APIRouter

from models.schemas import DecisionRequest, DecisionResponse
from services.decision_engine import decision_engine

router = APIRouter(prefix="/decision", tags=["decision"])


@router.post("", response_model=DecisionResponse)
async def decide(payload: DecisionRequest) -> DecisionResponse:
    return await decision_engine.decide(payload)
