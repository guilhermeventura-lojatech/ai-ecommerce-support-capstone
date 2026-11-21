import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MlSettings:
    confidence_threshold: float = 0.35
    min_known_token_ratio: float = 0.20

    @classmethod
    def from_environment(cls) -> "MlSettings":
        settings = cls(
            confidence_threshold=float(os.getenv("ML_CONFIDENCE_THRESHOLD", "0.35")),
            min_known_token_ratio=float(os.getenv("ML_MIN_KNOWN_TOKEN_RATIO", "0.20")),
        )
        if not 0 <= settings.confidence_threshold <= 1:
            raise ValueError("ML_CONFIDENCE_THRESHOLD deve estar entre 0 e 1.")
        if not 0 <= settings.min_known_token_ratio <= 1:
            raise ValueError("ML_MIN_KNOWN_TOKEN_RATIO deve estar entre 0 e 1.")
        return settings
