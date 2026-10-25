import re
import sys
from pathlib import Path

from inflation_file import FORMAT_VERSION, read_inflation
from months import month_after

FIRST_MONTH = "2010-01"
LOWEST_BASIS_POINTS = -1_000
HIGHEST_BASIS_POINTS = 5_000


def problems_of(inflation: dict) -> list[str]:
    problems = []
    if inflation.get("formatVersion") != FORMAT_VERSION:
        problems.append(f"formatVersion must be {FORMAT_VERSION}")
    months = inflation.get("months", [])
    problems += _problems_of_month_order(months)
    for entry in months:
        problems += _problems_of_month(entry)
    return problems


def _problems_of_month_order(months: list) -> list[str]:
    if not months:
        return ["months must not be empty"]
    names = [entry.get("month") for entry in months]
    if names[0] != FIRST_MONTH:
        return [f"months must start at {FIRST_MONTH}"]
    for previous, current in zip(names, names[1:]):
        if current != month_after(previous):
            return [f"{current} must come right after {previous}"]
    return []


def _problems_of_month(entry: dict) -> list[str]:
    month = entry.get("month")
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", str(month)):
        return [f"{month}: month must look like 2026-09"]
    value = entry.get("yearOnYearBasisPoints")
    if not (isinstance(value, int) and not isinstance(value, bool) and LOWEST_BASIS_POINTS <= value <= HIGHEST_BASIS_POINTS):
        return [f"{month}: yearOnYearBasisPoints must be between {LOWEST_BASIS_POINTS} and {HIGHEST_BASIS_POINTS}"]
    return []



def main(paths: list[str]) -> int:
    failed = False
    for path in paths:
        problems = problems_of(read_inflation(Path(path)))
        for problem in problems:
            print(f"{path}: {problem}")
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
