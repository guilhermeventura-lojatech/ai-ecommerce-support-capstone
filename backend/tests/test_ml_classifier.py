import pytest

from backend.app.ml.classifier import MlSettings, SklearnIntentClassifier
from backend.app.ml.dataset import load_dataset
from backend.app.schemas import Intent


@pytest.fixture(scope="module")
def classifier() -> SklearnIntentClassifier:
    return SklearnIntentClassifier(
        load_dataset(),
        settings=MlSettings(confidence_threshold=0.45, min_known_token_ratio=0.20),
    )


@pytest.mark.parametrize(
    ("message", "expected_intent"),
    [
        ("Minha encomenda deveria ter chegado ontem", Intent.DELIVERY),
        ("A blusa nao serviu e preciso de outro tamanho", Intent.EXCHANGE),
        ("Ainda aguardo o valor devolvido no meu cartao", Intent.REFUND),
        ("O banco recusou a cobranca na hora da compra", Intent.PAYMENT),
        ("Desisti e quero interromper esse pedido", Intent.CANCELLATION),
    ],
)
def test_classifier_recognizes_new_examples(
    classifier: SklearnIntentClassifier,
    message: str,
    expected_intent: Intent,
) -> None:
    result = classifier.classify(message)

    assert result.intent == expected_intent
    assert result.confidence > 0
    assert result.model_version.startswith("tfidf-logreg-")


def test_classifier_marks_unrelated_text_as_out_of_scope(
    classifier: SklearnIntentClassifier,
) -> None:
    result = classifier.classify("Qual a temperatura prevista para Marte no proximo domingo")

    assert result.is_out_of_scope is True

