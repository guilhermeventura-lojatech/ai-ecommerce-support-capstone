import re
import unicodedata
from dataclasses import dataclass
from typing import Sequence

from backend.app.knowledge.models import KnowledgeChunk
from backend.app.ports.llm_provider import GroundedAnswer


@dataclass(frozen=True)
class SafetyValidation:
    accepted: bool
    reason: str


def detect_prompt_injection(message: str) -> bool:
    normalized = _normalize(message)
    patterns = (
        r"ignore (?:as |todas as )?instrucoes",
        r"revele (?:o |seu )?prompt",
        r"system prompt",
        r"instrucoes anteriores",
        r"finja que (?:voce|e)",
    )
    return any(re.search(pattern, normalized) for pattern in patterns)


def validate_grounded_answer(
    answer: GroundedAnswer,
    chunks: Sequence[KnowledgeChunk],
    min_grounding_ratio: float = 0.35,
) -> SafetyValidation:
    text = answer.text.strip()
    if not text:
        return SafetyValidation(False, "EMPTY_ANSWER")
    authorized_ids = {chunk.source_id for chunk in chunks}
    cited_ids = set(answer.cited_source_ids)
    if not cited_ids or not cited_ids.issubset(authorized_ids):
        return SafetyValidation(False, "INVALID_OR_MISSING_CITATION")
    if _contains_forbidden_claim(text):
        return SafetyValidation(False, "FORBIDDEN_UNVERIFIABLE_CLAIM")

    answer_terms = _meaningful_terms(text)
    context_terms = _meaningful_terms(" ".join(chunk.content for chunk in chunks))
    if not answer_terms:
        return SafetyValidation(False, "ANSWER_WITHOUT_VERIFIABLE_CONTENT")
    grounding_ratio = len(answer_terms & context_terms) / len(answer_terms)
    if grounding_ratio < min_grounding_ratio:
        return SafetyValidation(False, "INSUFFICIENT_LEXICAL_GROUNDING")
    return SafetyValidation(True, "GROUNDED_AND_SAFE")


def _contains_forbidden_claim(text: str) -> bool:
    normalized = _normalize(text)
    forbidden_patterns = (
        r"r\$\s*\d",
        r"\b\d+\s*(?:dia|dias|hora|horas|semana|semanas)\b",
        r"(?:seu|o) pedido (?:esta|foi|sera) (?:enviado|entregue|cancelado|reembolsado)",
        r"(?:seu|o) reembolso (?:esta|foi|sera)",
    )
    return any(re.search(pattern, normalized) for pattern in forbidden_patterns)


def _meaningful_terms(text: str) -> set[str]:
    stopwords = {
        "a", "ao", "as", "com", "da", "de", "do", "e", "em", "o", "os",
        "para", "por", "que", "se", "um", "uma", "no", "na", "nos", "nas",
    }
    return {
        term
        for term in re.findall(r"[a-z0-9]+", _normalize(text))
        if len(term) > 2 and term not in stopwords
    }


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))
