from dataclasses import dataclass
from typing import Protocol

from backend.app.ml_settings import MlSettings

from backend.app.schemas import Intent


@dataclass(frozen=True)
class ClassificationResult:
    intent: Intent
    confidence: float
    model_version: str
    known_token_ratio: float
    is_out_of_scope: bool


class IntentClassifier(Protocol):
    """Contrato para classificadores locais de intencao."""

    settings: MlSettings

    def classify(self, message: str) -> ClassificationResult:
        ...

