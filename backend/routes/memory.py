from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from memory.semantic import semantic_memory
from models.schemas import MemoryItem, MemoryQuery

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=list[MemoryItem])
async def get_memory(user_id: UUID, query: str = "", top_k: int = 5) -> list[MemoryItem]:
    return await semantic_memory.retrieve_relevant_memory(user_id=user_id, query=query, top_k=top_k)


@router.post("", response_model=list[MemoryItem])
async def post_memory(request: MemoryQuery) -> list[MemoryItem]:
    return await semantic_memory.retrieve_relevant_memory(
        user_id=request.user_id,
        query=request.query,
        top_k=request.top_k,
    )
