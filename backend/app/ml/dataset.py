import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from sklearn.model_selection import train_test_split

from backend.app.schemas import Intent

DEFAULT_DATASET_PATH = Path(__file__).resolve().parents[3] / "data" / "intents_ecommerce_ptbr.csv"
SPLIT_SEED = 42


@dataclass(frozen=True)
class IntentExample:
    example_id: str
    message: str
    intent: Intent


@dataclass(frozen=True)
class DatasetSplit:
    train: tuple[IntentExample, ...]
    validation: tuple[IntentExample, ...]
    test: tuple[IntentExample, ...]


def normalize_for_deduplication(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"\w+", without_accents, flags=re.UNICODE))


def load_dataset(path: Path = DEFAULT_DATASET_PATH) -> tuple[IntentExample, ...]:
    examples: list[IntentExample] = []
    seen_messages: set[str] = set()
    seen_ids: set[str] = set()

    with path.open(encoding="utf-8", newline="") as dataset_file:
        for row in csv.DictReader(dataset_file):
            normalized = normalize_for_deduplication(row["mensagem"])
            if row["id"] in seen_ids:
                raise ValueError(f"ID duplicado no dataset: {row['id']}")
            if normalized in seen_messages:
                raise ValueError(f"Mensagem duplicada no dataset: {row['mensagem']}")
            seen_ids.add(row["id"])
            seen_messages.add(normalized)
            examples.append(
                IntentExample(
                    example_id=row["id"],
                    message=row["mensagem"],
                    intent=Intent(row["intencao"]),
                )
            )

    if not examples:
        raise ValueError("O dataset de intencoes esta vazio.")
    return tuple(examples)


def split_dataset(
    examples: tuple[IntentExample, ...], seed: int = SPLIT_SEED
) -> DatasetSplit:
    labels = [example.intent.value for example in examples]
    train, temporary = train_test_split(
        examples,
        test_size=0.30,
        random_state=seed,
        stratify=labels,
    )
    temporary_labels = [example.intent.value for example in temporary]
    validation, test = train_test_split(
        temporary,
        test_size=0.50,
        random_state=seed,
        stratify=temporary_labels,
    )
    return DatasetSplit(tuple(train), tuple(validation), tuple(test))

