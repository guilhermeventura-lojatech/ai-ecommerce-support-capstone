from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class GroundedAnswer:
    text: str
    sources: tuple[str, ...]


class ControlledLlmProvider(Protocol):
    """Interface futura; nenhum LLM e chamado na etapa 1."""

    def answer(self, message: str, authorized_context: Sequence[str]) -> GroundedAnswer:
        ...

