from time import perf_counter
from uuid import uuid4

from backend.app.knowledge.models import KnowledgeChunk
from backend.app.knowledge.retriever import LexicalKnowledgeRetriever
from backend.app.llm.provider import LlmProviderError
from backend.app.llm.safety import detect_prompt_injection, validate_grounded_answer
from backend.app.ml.classifier import SklearnIntentClassifier
from backend.app.ports.llm_provider import ControlledLlmProvider, GroundedAnswer
from backend.app.ports.ml_classifier import IntentClassifier
from backend.app.schemas import (
    AuditRecord,
    Intent,
    Route,
    SourceReference,
    SupportMessageRequest,
    SupportMessageResponse,
)
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
        retriever: LexicalKnowledgeRetriever | None = None,
        llm_provider: ControlledLlmProvider | None = None,
    ) -> None:
        self._rule_engine = rule_engine or RuleEngine()
        self._classifier = classifier or SklearnIntentClassifier.from_default_dataset()
        self._retriever = retriever or LexicalKnowledgeRetriever()
        self._llm_provider = llm_provider

    def route(self, request: SupportMessageRequest) -> SupportMessageResponse:
        started_at = perf_counter()
        correlation_id = uuid4()
        decision = self._rule_engine.evaluate(request.message)

        model_version = None
        ml_confidence = None
        ml_known_token_ratio = None
        ml_fallback_reason = None
        sources: list[SourceReference] = []
        llm_provider_name = None
        llm_model = None
        llm_answer: GroundedAnswer | None = None
        safety_result = None

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
                (
                    route,
                    answer,
                    reason_code,
                    ml_fallback_reason,
                    retrieved_chunks,
                    llm_answer,
                    safety_result,
                ) = self._route_with_authorized_knowledge(request.message, intent)
                sources = [
                    SourceReference(
                        source_id=chunk.source_id,
                        source_path=chunk.source_path,
                        score=chunk.score,
                    )
                    for chunk in retrieved_chunks
                ]
                if self._llm_provider is not None:
                    llm_provider_name = self._llm_provider.provider_name
                    llm_model = self._llm_provider.model_name
                if llm_answer is not None:
                    llm_provider_name = llm_answer.provider
                    llm_model = llm_answer.model
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
            sources=sources,
            llm_provider=llm_provider_name,
            llm_model=llm_model,
            llm_prompt_tokens=(llm_answer.usage.prompt_tokens if llm_answer else None),
            llm_completion_tokens=(
                llm_answer.usage.completion_tokens if llm_answer else None
            ),
            llm_total_tokens=(llm_answer.usage.total_tokens if llm_answer else None),
            llm_estimated_cost_usd=(
                llm_answer.usage.estimated_cost_usd if llm_answer else None
            ),
            safety_result=safety_result,
        )
        return SupportMessageResponse(
            correlation_id=correlation_id,
            route=route,
            intent=intent,
            answer=answer,
            requires_human=route == Route.HUMAN,
            audit=audit,
        )

    def _route_with_authorized_knowledge(
        self, message: str, intent: Intent
    ) -> tuple[
        Route,
        str,
        str,
        str,
        tuple[KnowledgeChunk, ...],
        GroundedAnswer | None,
        str | None,
    ]:
        if detect_prompt_injection(message):
            return (
                Route.HUMAN,
                HUMAN_FALLBACK_ANSWER,
                "PROMPT_INJECTION_DETECTED",
                "SECURITY_REJECTION",
                (),
                None,
                "PROMPT_INJECTION_DETECTED",
            )

        retrieval = self._retriever.retrieve(message)
        if retrieval.is_ambiguous:
            return (
                Route.HUMAN,
                HUMAN_FALLBACK_ANSWER,
                "AMBIGUOUS_AUTHORIZED_SOURCES",
                "AMBIGUOUS_RETRIEVAL",
                retrieval.chunks,
                None,
                "AMBIGUOUS_RETRIEVAL",
            )

        matching_chunks = tuple(
            chunk for chunk in retrieval.chunks if chunk.intent == intent
        )
        if not matching_chunks:
            return (
                Route.HUMAN,
                HUMAN_FALLBACK_ANSWER,
                "ML_INTENT_WITHOUT_AUTHORIZED_RESPONSE",
                "NO_AUTHORIZED_POLICY",
                retrieval.chunks,
                None,
                "NO_RELEVANT_AUTHORIZED_SOURCE",
            )
        if self._llm_provider is None:
            return (
                Route.HUMAN,
                HUMAN_FALLBACK_ANSWER,
                "LLM_DISABLED",
                "LLM_DISABLED",
                matching_chunks,
                None,
                "LLM_DISABLED_SAFE_FALLBACK",
            )

        try:
            generated = self._llm_provider.answer(message, matching_chunks)
        except (LlmProviderError, TimeoutError, OSError):
            return (
                Route.HUMAN,
                HUMAN_FALLBACK_ANSWER,
                "LLM_CALL_FAILED",
                "LLM_ERROR_OR_TIMEOUT",
                matching_chunks,
                None,
                "LLM_ERROR_OR_TIMEOUT",
            )

        validation = validate_grounded_answer(generated, matching_chunks)
        if not validation.accepted:
            return (
                Route.HUMAN,
                HUMAN_FALLBACK_ANSWER,
                "LLM_RESPONSE_NOT_VERIFIABLE",
                "LLM_SAFETY_REJECTION",
                matching_chunks,
                generated,
                validation.reason,
            )
        return (
            Route.LLM,
            generated.text,
            "GROUNDED_LLM_RESPONSE",
            "NONE",
            matching_chunks,
            generated,
            validation.reason,
        )
