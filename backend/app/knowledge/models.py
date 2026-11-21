from dataclasses import dataclass

from backend.app.schemas import Intent


@dataclass(frozen=True)
class KnowledgeChunk:
    source_id: str
    source_path: str
    content: str
    intent: Intent
    score: float = 0.0


@dataclass(frozen=True)
class RetrievalResult:
    chunks: tuple[KnowledgeChunk, ...]
    is_ambiguous: bool

