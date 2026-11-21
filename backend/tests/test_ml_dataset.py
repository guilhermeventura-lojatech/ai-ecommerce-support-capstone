from collections import Counter

from backend.app.ml.dataset import load_dataset, normalize_for_deduplication, split_dataset


def test_dataset_has_five_balanced_classes_without_duplicates() -> None:
    examples = load_dataset()
    class_counts = Counter(example.intent.value for example in examples)
    normalized_messages = {
        normalize_for_deduplication(example.message) for example in examples
    }

    assert len(examples) == 125
    assert set(class_counts.values()) == {25}
    assert len(normalized_messages) == len(examples)


def test_split_is_reproducible_stratified_and_has_no_leakage() -> None:
    examples = load_dataset()
    first = split_dataset(examples)
    second = split_dataset(examples)

    assert first == second
    assert (len(first.train), len(first.validation), len(first.test)) == (87, 19, 19)

    train_ids = {example.example_id for example in first.train}
    validation_ids = {example.example_id for example in first.validation}
    test_ids = {example.example_id for example in first.test}
    assert train_ids.isdisjoint(validation_ids)
    assert train_ids.isdisjoint(test_ids)
    assert validation_ids.isdisjoint(test_ids)
    assert train_ids | validation_ids | test_ids == {
        example.example_id for example in examples
    }

    for subset in (first.train, first.validation, first.test):
        assert {example.intent.value for example in subset} == {
            "entrega",
            "troca",
            "reembolso",
            "pagamento",
            "cancelamento",
        }

