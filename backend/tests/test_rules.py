import pytest

from backend.app.schemas import Intent, Route
from backend.app.services.rules import RuleEngine


@pytest.fixture
def engine() -> RuleEngine:
    return RuleEngine()


@pytest.mark.parametrize(
    "message",
    [
        "Como acompanhar meu pedido?",
        "Onde vejo o rastreio?",
        "Quero rastrear a encomenda",
    ],
)
def test_tracking_uses_authorized_rule(engine: RuleEngine, message: str) -> None:
    decision = engine.evaluate(message)

    assert decision is not None
    assert decision.route == Route.RULE
    assert decision.intent == Intent.DELIVERY
    assert decision.rule_id == "FAQ-TRACKING-001"
    assert "nao consulta pedidos" in decision.answer.casefold()


def test_exchange_is_recognized_but_escalated(engine: RuleEngine) -> None:
    decision = engine.evaluate("Quero trocar meu tenis")

    assert decision is not None
    assert decision.route == Route.HUMAN
    assert decision.intent == Intent.EXCHANGE
    assert "politica especifica" in decision.answer.casefold()


def test_refund_does_not_invent_deadline(engine: RuleEngine) -> None:
    decision = engine.evaluate("Quando recebo meu reembolso?")

    assert decision is not None
    assert decision.route == Route.HUMAN
    assert decision.intent == Intent.REFUND
    assert "nao ha prazo" in decision.answer.casefold()


def test_uncovered_message_has_no_rule(engine: RuleEngine) -> None:
    assert engine.evaluate("Meu pagamento foi recusado") is None

