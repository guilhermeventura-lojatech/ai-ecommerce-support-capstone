import os
from dataclasses import dataclass


def _as_bool(value: str) -> bool:
    return value.strip().casefold() in {"1", "true", "yes", "on", "sim"}


@dataclass(frozen=True)
class LlmSettings:
    enabled: bool = False
    provider: str = "openai_compatible"
    api_base_url: str = ""
    api_key: str = ""
    model: str = ""
    timeout_seconds: float = 10.0
    max_calls: int = 20
    max_input_tokens: int = 2_000
    max_output_tokens: int = 300
    max_budget_usd: float = 1.0
    input_cost_per_million_tokens: float = 0.0
    output_cost_per_million_tokens: float = 0.0

    @classmethod
    def from_environment(cls) -> "LlmSettings":
        settings = cls(
            enabled=_as_bool(os.getenv("LLM_ENABLED", "false")),
            provider=os.getenv("LLM_PROVIDER", "openai_compatible"),
            api_base_url=os.getenv("LLM_API_BASE_URL", ""),
            api_key=os.getenv("LLM_API_KEY", ""),
            model=os.getenv("LLM_MODEL", ""),
            timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "10")),
            max_calls=int(os.getenv("LLM_MAX_CALLS", "20")),
            max_input_tokens=int(os.getenv("LLM_MAX_INPUT_TOKENS", "2000")),
            max_output_tokens=int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "300")),
            max_budget_usd=float(os.getenv("LLM_MAX_BUDGET_USD", "1.00")),
            input_cost_per_million_tokens=float(
                os.getenv("LLM_INPUT_COST_PER_MILLION_TOKENS", "0")
            ),
            output_cost_per_million_tokens=float(
                os.getenv("LLM_OUTPUT_COST_PER_MILLION_TOKENS", "0")
            ),
        )
        if settings.timeout_seconds <= 0:
            raise ValueError("LLM_TIMEOUT_SECONDS deve ser positivo.")
        if min(settings.max_calls, settings.max_input_tokens, settings.max_output_tokens) <= 0:
            raise ValueError("Limites de chamadas e tokens devem ser positivos.")
        if settings.max_budget_usd < 0:
            raise ValueError("LLM_MAX_BUDGET_USD nao pode ser negativo.")
        return settings

    def validate_enabled_configuration(self) -> None:
        if not self.enabled:
            return
        if self.provider != "openai_compatible":
            raise ValueError("Somente o provedor openai_compatible e suportado nesta etapa.")
        if not self.api_base_url or not self.api_key or not self.model:
            raise ValueError(
                "LLM habilitado exige LLM_API_BASE_URL, LLM_API_KEY e LLM_MODEL."
            )

