from __future__ import annotations

from uuid import UUID

from models.schemas import MemoryItem
from services.database import database
from services.openai_client import openai_service


class SemanticMemory:
    async def store_memory(
        self,
        *,
        user_id: UUID,
        text: str,
        source_type: str,
        source_id: UUID | None = None,
    ) -> MemoryItem:
        """Store semantic memory with pgvector-backed embeddings."""
        embedding = await openai_service.embed(text)
        row = await database.fetchrow(
            """
            INSERT INTO semantic_memories (user_id, content, embedding, source_type, source_id)
            VALUES ($1, $2, $3::vector, $4, $5)
            RETURNING id, user_id, content, source_type, source_id, NULL::float AS similarity, created_at
            """,
            user_id,
            text,
            _format_vector(embedding),
            source_type,
            source_id,
        )
        assert row is not None
        return MemoryItem.model_validate(dict(row))

    async def retrieve_relevant_memory(self, user_id: UUID, query: str, top_k: int = 5) -> list[MemoryItem]:
        """Retrieve nearest semantic memories for a user query."""
        if not query:
            rows = await database.fetch(
                """
                SELECT id, user_id, content, source_type, source_id, NULL::float AS similarity, created_at
                FROM semantic_memories
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                user_id,
                top_k,
            )
            return [MemoryItem.model_validate(dict(row)) for row in rows]

        embedding = await openai_service.embed(query)
        rows = await database.fetch(
            """
            SELECT
                id,
                user_id,
                content,
                source_type,
                source_id,
                1 - (embedding <=> $2::vector) AS similarity,
                created_at
            FROM semantic_memories
            WHERE user_id = $1
            ORDER BY embedding <=> $2::vector
            LIMIT $3
            """,
            user_id,
            _format_vector(embedding),
            top_k,
        )
        return [MemoryItem.model_validate(dict(row)) for row in rows]


def _format_vector(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


semantic_memory = SemanticMemory()
