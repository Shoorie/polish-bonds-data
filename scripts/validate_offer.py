import re
import sys
from pathlib import Path

from offer_file import FORMAT_VERSION, SERIES_TERMS_IN_YEARS, read_offer

FAMILY_SERIES = {"ROS", "ROD"}
NOMINAL_PRICE_CENTS = 10_000


def problems_of(offer: dict) -> list[str]:
    problems = []
    problems += _problems_of_header(offer)
    problems += _problems_of_series_list(offer.get("series", []))
    for entry in offer.get("series", []):
        problems += _problems_of_series(entry)
    return problems


def _problems_of_header(offer: dict) -> list[str]:
    problems = []
    if offer.get("formatVersion") != FORMAT_VERSION:
        problems.append(f"formatVersion must be {FORMAT_VERSION}")
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", str(offer.get("month"))):
        problems.append("month must look like 2026-10")
    if not _is_within(offer.get("referenceRateBasisPoints"), 0, 2_000):
        problems.append("referenceRateBasisPoints must be between 0 and 2000")
    return problems


def _problems_of_series_list(series: list) -> list[str]:
    codes = [entry.get("code") for entry in series]
    if sorted(codes) != sorted(SERIES_TERMS_IN_YEARS):
        return [f"series must contain each of {sorted(SERIES_TERMS_IN_YEARS)} once, found {codes}"]
    return []


def _problems_of_series(entry: dict) -> list[str]:
    code = entry.get("code")
    problems = []
    if not re.fullmatch(rf"{code}\d{{4}}", str(entry.get("issueCode"))):
        problems.append(f"{code}: issueCode must look like {code}1036")
    if entry.get("termYears") != SERIES_TERMS_IN_YEARS.get(code):
        problems.append(f"{code}: termYears must be {SERIES_TERMS_IN_YEARS.get(code)}")
    if not _is_within(entry.get("firstPeriodRateBasisPoints"), 1, 2_000):
        problems.append(f"{code}: firstPeriodRateBasisPoints must be between 1 and 2000")
    if not _is_within(entry.get("marginBasisPoints"), 0, 1_000):
        problems.append(f"{code}: marginBasisPoints must be between 0 and 1000")
    if not _is_within(entry.get("earlyRedemptionFeeCents"), 0, 1_000):
        problems.append(f"{code}: earlyRedemptionFeeCents must be between 0 and 1000")
    if not _is_within(entry.get("exchangePriceCents"), 9_000, NOMINAL_PRICE_CENTS):
        problems.append(f"{code}: exchangePriceCents must be between 9000 and 10000")
    if code in FAMILY_SERIES and entry.get("exchangePriceCents") != NOMINAL_PRICE_CENTS:
        problems.append(f"{code}: family bonds are bought at the nominal price")
    return problems


def _is_within(value, lowest: int, highest: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and lowest <= value <= highest


def main(paths: list[str]) -> int:
    failed = False
    for path in paths:
        problems = problems_of(read_offer(Path(path)))
        for problem in problems:
            print(f"{path}: {problem}")
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
