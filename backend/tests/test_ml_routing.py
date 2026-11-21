from backend.app.ml_settings import MlSettings
from backend.app.ports.ml_classifier import ClassificationResult
from backend.app.schemas import Intent, Route, SupportMessageRequest
from backend.app.services.router import SupportRouter


class StubClassifier:
    def __init__(self, result: ClassificationResult, threshold: float = 0.45) -> None:
        self.result = result
        self.settings = MlSettings(
            confidence_threshold=threshold,
            min_known_token_ratio=0.20,
        )
        self.calls = 0

    def classify(self, message: str) -> ClassificationResult:
        self.calls += 1
        return self.result


def classification(
    intent: Intent,
    confidence: float,
    *,
    out_of_scope: bool = False,
) -> ClassificationResult:
    return ClassificationResult(
        intent=intent,
        confidence=confidence,
        model_version="stub-v1",
        known_token_ratio=0.0 if out_of_scope else 0.8,
        is_out_of_scope=out_of_scope,
    )


def test_rules_have_precedence_over_classifier() -> None:
    classifier = StubClassifier(classification(Intent.PAYMENT, 0.99))
    router = SupportRouter(classifier=classifier)

    response = router.route(SupportMessageRequest(message="Onde vejo o rastreio?"))

    assert response.route == Route.RULE
    assert response.intent == Intent.DELIVERY
    assert classifier.calls == 0
    assert response.audit.model_version is None


def test_high_confidence_intent_without_policy_is_escalated() -> None:
    classifier = StubClassifier(classification(Intent.PAYMENT, 0.91))
    router = SupportRouter(classifier=classifier)

    response = router.route(SupportMessageRequest(message="A cobranca falhou"))

    assert response.route == Route.HUMAN
    assert response.intent == Intent.PAYMENT
    assert response.audit.reason_code == "ML_INTENT_WITHOUT_AUTHORIZED_RESPONSE"
    assert response.audit.ml_fallback_reason == "NO_AUTHORIZED_POLICY"
    assert response.audit.ml_confidence == 0.91


def test_low_confidence_prediction_falls_back_to_unknown() -> None:
    classifier = StubClassifier(classification(Intent.CANCELLATION, 0.44))
    router = SupportRouter(classifier=classifier)

    response = router.route(SupportMessageRequest(message="Tenho uma duvida"))

    assert response.route == Route.HUMAN
    assert response.intent == Intent.UNKNOWN
    assert response.audit.ml_fallback_reason == "LOW_CONFIDENCE"


def test_out_of_scope_prediction_falls_back_to_unknown() -> None:
    classifier = StubClassifier(
        classification(Intent.DELIVERY, 0.88, out_of_scope=True)
    )
    router = SupportRouter(classifier=classifier)

    response = router.route(SupportMessageRequest(message="Quero uma receita de bolo"))

    assert response.route == Route.HUMAN
    assert response.intent == Intent.UNKNOWN
    assert response.audit.ml_fallback_reason == "OUT_OF_SCOPE"

