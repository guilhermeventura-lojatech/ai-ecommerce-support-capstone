import re
import unicodedata
from dataclasses import dataclass

from backend.app.schemas import Intent, Route

AUTHORIZED_FAQ_SOURCE = "knowledge/faq-exemplo.md"


@dataclass(frozen=True)
class RuleDecision:
    rule_id: str
    route: Route
    intent: Intent
    answer: str
    reason_code: str
    knowledge_source: str


class RuleEngine:
    """Regras limitadas ao conteudo explicitamente autorizado pela FAQ ficticia."""

    _tracking_patterns = (
        re.compile(r"\bacompanhar\b.*\bpedido\b"),
        re.compile(r"\brastre(?:io|ar|amento)\b"),
        re.compile(r"\bonde\b.*\b(?:pedido|encomenda)\b"),
    )
    _exchange_patterns = (
        re.compile(r"\btroc(?:a|ar|o)\b"),
        re.compile(r"\bdevolu(?:cao|cao|coes|ver)\b"),
    )
    _refund_patterns = (
        re.compile(r"\breembolso\b"),
        re.compile(r"\bdinheiro\b.*\bvolt(?:a|ar)\b"),
        re.compile(r"\bestorno\b"),
    )

    def evaluate(self, message: str) -> RuleDecision | None:
        normalized = self._normalize(message)

        if self._matches(normalized, self._tracking_patterns):
            return RuleDecision(
                rule_id="FAQ-TRACKING-001",
                route=Route.RULE,
                intent=Intent.DELIVERY,
                answer=(
                    "Para acompanhar um pedido, tenha o numero do pedido em maos e use "
                    "o canal autorizado da loja. Este prototipo nao consulta pedidos nem "
                    "sistemas reais."
                ),
                reason_code="AUTHORIZED_FAQ_TRACKING_GUIDANCE",
                knowledge_source=AUTHORIZED_FAQ_SOURCE,
            )

        if self._matches(normalized, self._exchange_patterns):
            return RuleDecision(
                rule_id="FAQ-EXCHANGE-ESCALATE-001",
                route=Route.HUMAN,
                intent=Intent.EXCHANGE,
                answer=(
                    "A politica especifica de trocas nao esta disponivel neste prototipo. "
                    "Sua solicitacao deve ser encaminhada para atendimento humano."
                ),
                reason_code="EXCHANGE_POLICY_NOT_AUTHORIZED",
                knowledge_source=AUTHORIZED_FAQ_SOURCE,
            )

        if self._matches(normalized, self._refund_patterns):
            return RuleDecision(
                rule_id="FAQ-REFUND-ESCALATE-001",
                route=Route.HUMAN,
                intent=Intent.REFUND,
                answer=(
                    "Nao ha prazo de reembolso autorizado para informar neste prototipo. "
                    "Sua solicitacao deve ser encaminhada para atendimento humano."
                ),
                reason_code="REFUND_DEADLINE_NOT_AUTHORIZED",
                knowledge_source=AUTHORIZED_FAQ_SOURCE,
            )

        return None

    @staticmethod
    def _matches(message: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
        return any(pattern.search(message) for pattern in patterns)

    @staticmethod
    def _normalize(message: str) -> str:
        decomposed = unicodedata.normalize("NFKD", message.casefold())
        without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
        return " ".join(without_accents.split())

