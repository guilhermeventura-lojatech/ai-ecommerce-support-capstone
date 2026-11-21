from backend.app.knowledge.retriever import LexicalKnowledgeRetriever
from backend.app.schemas import Intent


def test_retriever_returns_authorized_chunk_with_traceable_source() -> None:
    result = LexicalKnowledgeRetriever().retrieve(
        "Como posso acompanhar o pedido pelo canal autorizado"
    )

    assert result.is_ambiguous is False
    assert result.chunks
    chunk = result.chunks[0]
    assert chunk.source_id == "faq-001-acompanhar-pedido"
    assert chunk.source_path == "knowledge/faq-exemplo.md"
    assert chunk.intent == Intent.DELIVERY
    assert chunk.score >= 0.18


def test_retriever_returns_no_source_for_unrelated_question() -> None:
    result = LexicalKnowledgeRetriever().retrieve(
        "Quero conversar sobre astronomia e culinaria"
    )

    assert result.chunks == ()
    assert result.is_ambiguous is False

