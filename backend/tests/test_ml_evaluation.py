from backend.app.ml.dataset import load_dataset, split_dataset
from backend.app.ml.evaluation import LABELS, run_evaluation


def test_evaluation_is_reproducible_and_matrix_has_expected_shape() -> None:
    split = split_dataset(load_dataset())
    first = run_evaluation(split)
    second = run_evaluation(split)

    assert first == second
    assert first["validation"].sample_count == 19
    assert first["test"].sample_count == 19
    assert len(first["test"].confusion_matrix) == len(LABELS) == 5
    assert all(len(row) == 5 for row in first["test"].confusion_matrix)
    assert sum(map(sum, first["test"].confusion_matrix)) == 19
    assert 0 <= first["test"].macro_f1 <= 1

