import re
import sys
from datetime import date
from pathlib import Path

from reference_rates_file import FORMAT_VERSION, read_reference_rates

FIRST_DAY = "2016-11-01"
HIGHEST_BASIS_POINTS = 2_000


def problems_of(reference_rates: dict) -> list[str]:
    problems = []
    if reference_rates.get("formatVersion") != FORMAT_VERSION:
        problems.append(f"formatVersion must be {FORMAT_VERSION}")
    changes = reference_rates.get("changes", [])
    for entry in changes:
        problems += _problems_of_change(entry)
    if not problems:
        problems += _problems_of_change_order(changes)
    return problems


def _problems_of_change(entry: dict) -> list[str]:
    day = entry.get("effectiveFrom")
    if not _is_day(day):
        return [f"{day}: effectiveFrom must look like 2026-03-05"]
    value = entry.get("basisPoints")
    if not (isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= HIGHEST_BASIS_POINTS):
        return [f"{day}: basisPoints must be between 0 and {HIGHEST_BASIS_POINTS}"]
    return []


def _problems_of_change_order(changes: list) -> list[str]:
    if not changes:
        return ["changes must not be empty"]
    if changes[0]["effectiveFrom"] > FIRST_DAY:
        return [f"changes must start with the rate in force on {FIRST_DAY}"]
    for previous, current in zip(changes, changes[1:]):
        if current["effectiveFrom"] <= previous["effectiveFrom"]:
            return [f"{current['effectiveFrom']} must come after {previous['effectiveFrom']}"]
        if current["basisPoints"] == previous["basisPoints"]:
            return [f"{current['effectiveFrom']} repeats the rate of {previous['effectiveFrom']}"]
    return []


def _is_day(value) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def main(paths: list[str]) -> int:
    failed = False
    for path in paths:
        problems = problems_of(read_reference_rates(Path(path)))
        for problem in problems:
            print(f"{path}: {problem}")
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
