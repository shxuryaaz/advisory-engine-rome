from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings


class OpenAIService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            self.client: AsyncOpenAI | None = None
        else:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    async def complete_json(self, system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            return self._fallback_agent_response(user_payload)

        response = await self.client.chat.completions.create(
            model=settings.openai_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, default=str)},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    async def json_completion(self, prompt: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self.complete_json(prompt, payload or {})

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    async def embed(self, text: str) -> list[float]:
        if self.client is None:
            # Deterministic zero vector keeps local/dev API usable without secrets.
            return [0.0] * 1536

        response = await self.client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding

    @staticmethod
    def _fallback_agent_response(payload: dict[str, Any]) -> dict[str, Any]:
        agent = payload.get("agent", "strategist")
        return {
            "agent": agent,
            "score": 0.5,
            "reasoning": "OpenAI API key is not configured; returning neutral development-mode assessment.",
            "warnings": ["Configure OPENAI_API_KEY for production agent reasoning."],
        }


openai_service = OpenAIService()
