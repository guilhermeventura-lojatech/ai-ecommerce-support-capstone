from dataclasses import dataclass

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

from backend.app.ml.classifier import build_pipeline
from backend.app.ml.dataset import DatasetSplit, IntentExample
from backend.app.schemas import Intent

LABELS = tuple(intent.value for intent in Intent if intent is not Intent.UNKNOWN)


@dataclass(frozen=True)
class EvaluationMetrics:
    sample_count: int
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    per_class: dict[str, dict[str, float]]
    confusion_matrix: tuple[tuple[int, ...], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "sample_count": self.sample_count,
            "accuracy": self.accuracy,
            "macro_precision": self.macro_precision,
            "macro_recall": self.macro_recall,
            "macro_f1": self.macro_f1,
            "per_class": self.per_class,
            "labels": list(LABELS),
            "confusion_matrix": [list(row) for row in self.confusion_matrix],
        }


def run_evaluation(split: DatasetSplit) -> dict[str, EvaluationMetrics]:
    pipeline = build_pipeline()
    pipeline.fit(
        [example.message for example in split.train],
        [example.intent.value for example in split.train],
    )
    return {
        "validation": evaluate_examples(pipeline, split.validation),
        "test": evaluate_examples(pipeline, split.test),
    }


def evaluate_examples(pipeline: object, examples: tuple[IntentExample, ...]) -> EvaluationMetrics:
    expected = [example.intent.value for example in examples]
    predicted = pipeline.predict([example.message for example in examples])
    precision, recall, f1, _ = precision_recall_fscore_support(
        expected,
        predicted,
        labels=LABELS,
        average="macro",
        zero_division=0,
    )
    per_class_precision, per_class_recall, per_class_f1, _ = (
        precision_recall_fscore_support(
            expected,
            predicted,
            labels=LABELS,
            average=None,
            zero_division=0,
        )
    )
    matrix = confusion_matrix(expected, predicted, labels=LABELS)
    return EvaluationMetrics(
        sample_count=len(examples),
        accuracy=float(accuracy_score(expected, predicted)),
        macro_precision=float(precision),
        macro_recall=float(recall),
        macro_f1=float(f1),
        per_class={
            label: {
                "precision": float(per_class_precision[index]),
                "recall": float(per_class_recall[index]),
                "f1": float(per_class_f1[index]),
            }
            for index, label in enumerate(LABELS)
        },
        confusion_matrix=tuple(tuple(int(value) for value in row) for row in matrix),
    )

