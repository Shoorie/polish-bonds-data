import sys
from pathlib import Path

from months import month_after
from offer_file import FORMAT_VERSION, read_offer, read_offer_months
from reference_rate import rate_on
from reference_rates_file import changes_of, read_reference_rates

FIRST_MONTH = "2016-11"


def problems_of_archive(folder: Path) -> list[str]:
    offer_months = read_offer_months(folder / "offer-months.json")
    months = offer_months.get("months", [])
    problems = []
    if offer_months.get("formatVersion") != FORMAT_VERSION:
        problems.append(f"offer-months.json: formatVersion must be {FORMAT_VERSION}")
    problems += _problems_of_month_order(months)
    files = sorted(path.stem for path in (folder / "offers").glob("*.json"))
    if files != months:
        problems.append("offer-months.json must list exactly the months in offers/")
    if months and read_offer(folder / "offer.json") != read_offer(folder / "offers" / f"{months[-1]}.json"):
        problems.append(f"offer.json must be the same as offers/{months[-1]}.json")
    problems += _problems_of_reference_rates(folder, files)
    return problems


def _problems_of_month_order(months: list) -> list[str]:
    if not months or months[0] != FIRST_MONTH:
        return [f"offer-months.json must start at {FIRST_MONTH}"]
    for previous, current in zip(months, months[1:]):
        if current != month_after(previous):
            return [f"offer-months.json: {current} must come right after {previous}"]
    return []


def _problems_of_reference_rates(folder: Path, months: list[str]) -> list[str]:
    changes = changes_of(read_reference_rates(folder / "reference-rates.json"))
    problems = []
    for month in months:
        expected = rate_on(changes, f"{month}-01")
        if read_offer(folder / "offers" / f"{month}.json")["referenceRateBasisPoints"] != expected:
            problems.append(f"offers/{month}.json: referenceRateBasisPoints must be {expected}, the rate on {month}-01")
    return problems



def main(folder: str) -> int:
    problems = problems_of_archive(Path(folder))
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
