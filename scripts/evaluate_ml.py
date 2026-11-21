import json

from backend.app.ml.dataset import SPLIT_SEED, load_dataset, split_dataset
from backend.app.ml.evaluation import run_evaluation


def main() -> None:
    examples = load_dataset()
    split = split_dataset(examples)
    metrics = run_evaluation(split)
    report = {
        "dataset_size": len(examples),
        "seed": SPLIT_SEED,
        "split_sizes": {
            "train": len(split.train),
            "validation": len(split.validation),
            "test": len(split.test),
        },
        "metrics": {name: result.as_dict() for name, result in metrics.items()},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
