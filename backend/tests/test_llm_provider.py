import json

import pytest

from backend.app.knowledge.models import KnowledgeChunk
from backend.app.llm.provider import LlmLimitError, OpenAiCompatibleLlmProvider
from backend.app.llm.settings import LlmSettings
from backend.app.schemas import Intent


def settings(**overrides: object) -> LlmSettings:
    values = {
        "enabled": True,
        "provider": "openai_compatible",
        "api_base_url": "https://invalid.example.test/chat",
        "api_key": "test-secret-not-real",
        "model": "test-model",
        "max_calls": 1,
        "max_input_tokens": 2_000,
        "max_output_tokens": 100,
        "max_budget_usd": 1.0,
        "input_cost_per_million_tokens": 1.0,
        "output_cost_per_million_tokens": 2.0,
    }
    values.update(overrides)
    return LlmSettings(**values)


def chunk() -> KnowledgeChunk:
    return KnowledgeChunk(
        source_id="faq-001-acompanhar-pedido",
        source_path="knowledge/faq-exemplo.md",
        content="Solicite o numero do pedido pelo canal autorizado.",
        intent=Intent.DELIVERY,
        score=0.9,
    )


def test_provider_parses_structured_answer_without_real_api_call() -> None:
    def fake_sender(request: object, timeout: float) -> dict[str, object]:
        assert timeout == 10.0
        payload = json.loads(request.data.decode("utf-8"))
        assert "test-secret-not-real" not in json.dumps(payload)
        assert "Solicite o numero" in json.dumps(payload)
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "answer": "Solicite o numero do pedido pelo canal autorizado.",
                                "cited_source_ids": ["faq-001-acompanhar-pedido"],
                            }
                        )
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 10,
                "total_tokens": 60,
            },
        }

    provider = OpenAiCompatibleLlmProvider(settings(), request_sender=fake_sender)
    result = provider.answer("Como consulto?", (chunk(),))

    assert result.provider == "openai_compatible"
    assert result.model == "test-model"
    assert result.usage.total_tokens == 60
    assert result.usage.estimated_cost_usd == pytest.approx(0.00007)


def test_provider_enforces_call_limit_without_external_request() -> None:
    calls = 0

    def fake_sender(request: object, timeout: float) -> dict[str, object]:
        nonlocal calls
        calls += 1
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "answer": "Solicite o numero do pedido.",
                                "cited_source_ids": ["faq-001-acompanhar-pedido"],
                            }
                        )
                    }
                }
            ]
        }

    provider = OpenAiCompatibleLlmProvider(settings(), request_sender=fake_sender)
    provider.answer("Como consulto?", (chunk(),))

    with pytest.raises(LlmLimitError):
        provider.answer("Como consulto novamente?", (chunk(),))
    assert calls == 1

