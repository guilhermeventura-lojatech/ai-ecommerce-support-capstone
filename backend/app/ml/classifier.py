import hashlib
import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from backend.app.ml.dataset import DEFAULT_DATASET_PATH, IntentExample, load_dataset
from backend.app.ml_settings import MlSettings
from backend.app.ports.ml_classifier import ClassificationResult, IntentClassifier
from backend.app.schemas import Intent

MODEL_CONFIG = {
    "algorithm": "LogisticRegression",
    "C": 1.0,
    "class_weight": "balanced",
    "max_iter": 1_000,
    "random_state": 42,
    "tfidf_ngram_range": (1, 2),
    "tfidf_strip_accents": "unicode",
    "tfidf_sublinear_tf": True,
}


class SklearnIntentClassifier(IntentClassifier):
    def __init__(
        self,
        examples: tuple[IntentExample, ...],
        settings: MlSettings | None = None,
        dataset_path: Path = DEFAULT_DATASET_PATH,
    ) -> None:
        self.settings = settings or MlSettings.from_environment()
        self._pipeline = build_pipeline()
        self._pipeline.fit(
            [example.message for example in examples],
            [example.intent.value for example in examples],
        )
        self._vectorizer: TfidfVectorizer = self._pipeline.named_steps["tfidf"]
        self._analyzer = self._vectorizer.build_analyzer()
        self.model_version = _model_version(dataset_path, self.settings)

    @classmethod
    def from_default_dataset(cls) -> "SklearnIntentClassifier":
        return cls(load_dataset())

    def classify(self, message: str) -> ClassificationResult:
        probabilities = self._pipeline.predict_proba([message])[0]
        best_index = int(probabilities.argmax())
        predicted_label = str(self._pipeline.classes_[best_index])
        confidence = float(probabilities[best_index])

        tokens = self._analyzer(message)
        known_tokens = sum(token in self._vectorizer.vocabulary_ for token in tokens)
        known_token_ratio = known_tokens / len(tokens) if tokens else 0.0
        is_out_of_scope = known_token_ratio <= self.settings.min_known_token_ratio

        return ClassificationResult(
            intent=Intent(predicted_label),
            confidence=confidence,
            model_version=self.model_version,
            known_token_ratio=known_token_ratio,
            is_out_of_scope=is_out_of_scope,
        )


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=1,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    C=MODEL_CONFIG["C"],
                    max_iter=1_000,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def _model_version(dataset_path: Path, settings: MlSettings) -> str:
    digest = hashlib.sha256()
    digest.update(dataset_path.read_bytes())
    digest.update(json.dumps(settings.__dict__, sort_keys=True).encode("utf-8"))
    digest.update(json.dumps(MODEL_CONFIG, sort_keys=True).encode("utf-8"))
    return f"tfidf-logreg-{digest.hexdigest()[:12]}"

