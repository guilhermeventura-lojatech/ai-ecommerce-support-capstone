import re
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.knowledge.models import KnowledgeChunk, RetrievalResult
from backend.app.schemas import Intent

AUTHORIZED_FAQ_PATH = Path(__file__).resolve().parents[3] / "knowledge" / "faq-exemplo.md"
AUTHORIZED_SOURCE_PATH = "knowledge/faq-exemplo.md"


@dataclass(frozen=True)
class RetrievalSettings:
    min_score: float = 0.18
    ambiguity_margin: float = 0.05
    max_chunks: int = 2


class LexicalKnowledgeRetriever:
    def __init__(
        self,
        faq_path: Path = AUTHORIZED_FAQ_PATH,
        settings: RetrievalSettings | None = None,
    ) -> None:
        self.settings = settings or RetrievalSettings()
        self._chunks = _load_authorized_faq(faq_path)
        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        self._matrix = self._vectorizer.fit_transform(
            chunk.content for chunk in self._chunks
        )

    def retrieve(self, query: str) -> RetrievalResult:
        query_vector = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self._matrix)[0]
        ranked_indexes = sorted(range(len(scores)), key=lambda index: scores[index], reverse=True)
        relevant = tuple(
            replace(self._chunks[index], score=float(scores[index]))
            for index in ranked_indexes[: self.settings.max_chunks]
            if scores[index] >= self.settings.min_score
        )
        ambiguous = (
            len(relevant) >= 2
            and relevant[0].intent != relevant[1].intent
            and relevant[0].score - relevant[1].score <= self.settings.ambiguity_margin
        )
        return RetrievalResult(chunks=relevant, is_ambiguous=ambiguous)


def _load_authorized_faq(path: Path) -> tuple[KnowledgeChunk, ...]:
    chunks: list[KnowledgeChunk] = []
    bullet_pattern = re.compile(r"^- \*\*(.+?)\*\*\s*(.+)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = bullet_pattern.match(line.strip())
        if not match:
            continue
        question, answer = match.groups()
        normalized_question = _normalize(question)
        if "acompanhar pedido" in normalized_question:
            source_id, intent = "faq-001-acompanhar-pedido", Intent.DELIVERY
        elif "trocar um produto" in normalized_question:
            source_id, intent = "faq-002-troca", Intent.EXCHANGE
        elif "reembolso" in normalized_question:
            source_id, intent = "faq-003-reembolso", Intent.REFUND
        else:
            continue
        chunks.append(
            KnowledgeChunk(
                source_id=source_id,
                source_path=AUTHORIZED_SOURCE_PATH,
                content=f"{question} {answer}",
                intent=intent,
            )
        )
    if len(chunks) != 3:
        raise ValueError("A FAQ autorizada deve produzir exatamente tres trechos conhecidos.")
    return tuple(chunks)


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))

