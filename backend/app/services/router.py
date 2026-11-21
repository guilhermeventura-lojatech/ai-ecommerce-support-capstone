from time import perf_counter
from uuid import uuid4

from backend.app.schemas import (
    AuditRecord,
    Intent,
    Route,
    SupportMessageRequest,
    SupportMessageResponse,
)
from backend.app.ml.classifier import SklearnIntentClassifier
from backend.app.ports.ml_classifier import IntentClassifier
from backend.app.services.rules import RuleEngine

HUMAN_FALLBACK_ANSWER = (
    "Nao ha informacao autorizada suficiente para responder automaticamente. "
    "Sua solicitacao deve ser encaminhada para atendimento humano."
)


class SupportRouter:
    def __init__(
        self,
        rule_engine: RuleEngine | None = None,
        classifier: IntentClassifier | None = None,
    ) -> None:
        self._rule_engine = rule_engine or RuleEngine()
        self._classifier = classifier or SklearnIntentClassifier.from_default_dataset()

    def route(self, request: SupportMessageRequest) -> SupportMessageResponse:
        started_at = perf_counter()
        correlation_id = uuid4()
        decision = self._rule_engine.evaluate(request.message)

        model_version = None
        ml_confidence = None
        ml_known_token_ratio = None
        ml_fallback_reason = None

        if decision is None:
            classification = self._classifier.classify(request.message)
            model_version = classification.model_version
            ml_confidence = classification.confidence
            ml_known_token_ratio = classification.known_token_ratio
            route = Route.HUMAN
            answer = HUMAN_FALLBACK_ANSWER
            rule_id = None
            knowledge_source = None

            if classification.is_out_of_scope:
                intent = Intent.UNKNOWN
                reason_code = "NO_AUTHORIZED_RULE_MATCH"
                ml_fallback_reason = "OUT_OF_SCOPE"
            elif classification.confidence < self._classifier.settings.confidence_threshold:
                intent = Intent.UNKNOWN
                reason_code = "NO_AUTHORIZED_RULE_MATCH"
                ml_fallback_reason = "LOW_CONFIDENCE"
            else:
                intent = classification.intent
                reason_code = "ML_INTENT_WITHOUT_AUTHORIZED_RESPONSE"
                ml_fallback_reason = "NO_AUTHORIZED_POLICY"
        else:
            route = decision.route
            intent = decision.intent
            answer = decision.answer
            reason_code = decision.reason_code
            rule_id = decision.rule_id
            knowledge_source = decision.knowledge_source

        duration_ms = (perf_counter() - started_at) * 1_000
        audit = AuditRecord(
            correlation_id=correlation_id,
            route=route,
            reason_code=reason_code,
            duration_ms=duration_ms,
            rule_id=rule_id,
            knowledge_source=knowledge_source,
            model_version=model_version,
            ml_confidence=ml_confidence,
            ml_known_token_ratio=ml_known_token_ratio,
            ml_fallback_reason=ml_fallback_reason,
        )
        return SupportMessageResponse(
            correlation_id=correlation_id,
            route=route,
            intent=intent,
            answer=answer,
            requires_human=route == Route.HUMAN,
            audit=audit,
        )

