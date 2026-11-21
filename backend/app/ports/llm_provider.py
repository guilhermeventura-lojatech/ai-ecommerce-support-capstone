from dataclasses import dataclass
from typing import Protocol, Sequence

from backend.app.knowledge.models import KnowledgeChunk


@dataclass(frozen=True)
class LlmUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost_usd: float | None = None


@dataclass(frozen=True)
class GroundedAnswer:
    text: str
    cited_source_ids: tuple[str, ...]
    provider: str
    model: str
    usage: LlmUsage


class ControlledLlmProvider(Protocol):
    """Contrato para um LLM opcional que recebe somente contexto autorizado."""

    provider_name: str
    model_name: str

    def answer(
        self, message: str, authorized_context: Sequence[KnowledgeChunk]
    ) -> GroundedAnswer:
        ...

