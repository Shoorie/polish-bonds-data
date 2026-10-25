import json
from pathlib import Path

from reference_rate import RateChange

FORMAT_VERSION = 1


def reference_rates_of(changes: list[RateChange]) -> dict:
    return {
        "formatVersion": FORMAT_VERSION,
        "changes": [_change_entry(change) for change in changes],
    }


def write_reference_rates(reference_rates: dict, folder: Path) -> None:
    content = json.dumps(reference_rates, ensure_ascii=False, indent=2) + "\n"
    (folder / "reference-rates.json").write_text(content, encoding="utf-8")


def read_reference_rates(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def changes_of(reference_rates: dict) -> list[RateChange]:
    return [
        RateChange(effective_from=entry["effectiveFrom"], basis_points=entry["basisPoints"])
        for entry in reference_rates["changes"]
    ]


def _change_entry(change: RateChange) -> dict:
    return {
        "effectiveFrom": change.effective_from,
        "basisPoints": change.basis_points,
    }
