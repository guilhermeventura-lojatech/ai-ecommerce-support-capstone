from dataclasses import dataclass
from typing import Protocol

from backend.app.schemas import Intent


@dataclass(frozen=True)
class ClassificationResult:
    intent: Intent
    confidence: float
    model_version: str


class IntentClassifier(Protocol):
    """Interface futura; nenhuma classificacao ML e executada na etapa 1."""

    def classify(self, message: str) -> ClassificationResult:
        ...

