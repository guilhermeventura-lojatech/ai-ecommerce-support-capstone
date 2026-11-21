import json

from backend.app.ml.classifier import SklearnIntentClassifier
from backend.app.ml.dataset import load_dataset, split_dataset
from backend.app.ml_settings import MlSettings
from backend.app.services.rules import RuleEngine


def main() -> None:
    split = split_dataset(load_dataset())
    classifier = SklearnIntentClassifier(split.train, settings=MlSettings())
    rule_engine = RuleEngine()

    expected: list[str] = []
    rules_predictions: list[str] = []
    hybrid_predictions: list[str] = []
    raw_hybrid_predictions: list[str] = []
    fallback_count = 0

    for example in split.test:
        expected.append(example.intent.value)
        rule = rule_engine.evaluate(example.message)
        classification = classifier.classify(example.message)

        rules_prediction = rule.intent.value if rule else "desconhecida"
        rules_predictions.append(rules_prediction)
        raw_hybrid_predictions.append(
            rule.intent.value if rule else classification.intent.value
        )

        rejected = (
            classification.is_out_of_scope
            or classification.confidence < classifier.settings.confidence_threshold
        )
        if rule:
            hybrid_predictions.append(rule.intent.value)
        elif rejected:
            hybrid_predictions.append("desconhecida")
            fallback_count += 1
        else:
            hybrid_predictions.append(classification.intent.value)

    report = {
        "scope": "conjunto sintetico de teste rotulado",
        "sample_count": len(expected),
        "rules_only": summarize(expected, rules_predictions),
        "rules_plus_ml_with_safety_thresholds": {
            **summarize(expected, hybrid_predictions),
            "fallback_count": fallback_count,
        },
        "rules_plus_raw_ml_diagnostic_only": summarize(
            expected, raw_hybrid_predictions
        ),
        "warning": (
            "A linha diagnostica ignora thresholds e nao representa o "
            "comportamento seguro da API."
        ),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


def summarize(expected: list[str], predicted: list[str]) -> dict[str, float | int]:
    correct = sum(actual == prediction for actual, prediction in zip(expected, predicted))
    covered = sum(prediction != "desconhecida" for prediction in predicted)
    return {
        "covered": covered,
        "correct": correct,
        "accuracy_over_all_cases": correct / len(expected),
        "coverage": covered / len(expected),
    }


if __name__ == "__main__":
    main()
