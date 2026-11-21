from time import perf_counter
from uuid import uuid4

from backend.app.schemas import (
    AuditRecord,
    Intent,
    Route,
    SupportMessageRequest,
    SupportMessageResponse,
)
from backend.app.services.rules import RuleEngine

HUMAN_FALLBACK_ANSWER = (
    "Nao ha informacao autorizada suficiente para responder automaticamente. "
    "Sua solicitacao deve ser encaminhada para atendimento humano."
)


class SupportRouter:
    def __init__(self, rule_engine: RuleEngine | None = None) -> None:
        self._rule_engine = rule_engine or RuleEngine()

    def route(self, request: SupportMessageRequest) -> SupportMessageResponse:
        started_at = perf_counter()
        correlation_id = uuid4()
        decision = self._rule_engine.evaluate(request.message)

        if decision is None:
            route = Route.HUMAN
            intent = Intent.UNKNOWN
            answer = HUMAN_FALLBACK_ANSWER
            reason_code = "NO_AUTHORIZED_RULE_MATCH"
            rule_id = None
            knowledge_source = None
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
        )
        return SupportMessageResponse(
            correlation_id=correlation_id,
            route=route,
            intent=intent,
            answer=answer,
            requires_human=route == Route.HUMAN,
            audit=audit,
        )

