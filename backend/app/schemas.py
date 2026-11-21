from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Intent(str, Enum):
    DELIVERY = "entrega"
    EXCHANGE = "troca"
    REFUND = "reembolso"
    PAYMENT = "pagamento"
    CANCELLATION = "cancelamento"
    UNKNOWN = "desconhecida"


class Route(str, Enum):
    RULE = "regra"
    HUMAN = "humano"
    ML = "ml"
    LLM = "llm"


class SupportMessageRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=2_000)

    @field_validator("message")
    @classmethod
    def reject_blank_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A mensagem nao pode conter apenas espacos.")
        return value


class SourceReference(BaseModel):
    source_id: str
    source_path: str
    score: float = Field(ge=0, le=1)


class AuditRecord(BaseModel):
    correlation_id: UUID
    route: Route
    reason_code: str
    duration_ms: float = Field(ge=0)
    rule_id: str | None = None
    knowledge_source: str | None = None
    model_version: str | None = None
    ml_confidence: float | None = Field(default=None, ge=0, le=1)
    ml_known_token_ratio: float | None = Field(default=None, ge=0, le=1)
    ml_fallback_reason: str | None = None
    sources: list[SourceReference] = Field(default_factory=list)
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_prompt_tokens: int | None = Field(default=None, ge=0)
    llm_completion_tokens: int | None = Field(default=None, ge=0)
    llm_total_tokens: int | None = Field(default=None, ge=0)
    llm_estimated_cost_usd: float | None = Field(default=None, ge=0)
    safety_result: str | None = None


class SupportMessageResponse(BaseModel):
    correlation_id: UUID
    route: Route
    intent: Intent
    answer: str
    requires_human: bool
    audit: AuditRecord


class HealthResponse(BaseModel):
    status: str
    stage: str

