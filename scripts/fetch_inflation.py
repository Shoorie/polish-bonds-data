import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from gus_indicator import MonthlyInflation, read_monthly_inflation
from inflation_file import inflation_of, read_inflation, write_inflation

GUS_INDICATOR_DATA = "https://api-sdp.stat.gov.pl/api/indicators/indicator-data-indicator"
FIRST_YEAR = 2010
LAST_YEAR_OF_OLD_CLASSIFICATION = 2025
OLD_CLASSIFICATION_INDICATOR = 1832
COICOP_2018_INDICATOR = 2728
PAUSE_BETWEEN_REQUESTS_SECONDS = 1
INFLATION_FOLDER = Path(__file__).resolve().parent.parent / "v1"


def main() -> int:
    months = [inflation for year in range(FIRST_YEAR, date.today().year + 1) for inflation in _months_of(year)]
    inflation = inflation_of(months)
    if inflation == _current_inflation():
        print("Inflation unchanged")
        return 0

    write_inflation(inflation, INFLATION_FOLDER)
    print(f"Inflation updated to {months[-1].month}")
    return 0


def _current_inflation() -> dict | None:
    current = INFLATION_FOLDER / "inflation.json"
    return read_inflation(current) if current.exists() else None


def _months_of(year: int) -> list[MonthlyInflation]:
    time.sleep(PAUSE_BETWEEN_REQUESTS_SECONDS)
    try:
        indicator_data = _download(f"{GUS_INDICATOR_DATA}?id-wskaznik={_indicator_of(year)}&id-rok={year}&lang=pl")
    except urllib.error.HTTPError as error:
        if error.code == 404 and year == date.today().year:
            return []
        raise
    return read_monthly_inflation(indicator_data)


def _indicator_of(year: int) -> int:
    if year <= LAST_YEAR_OF_OLD_CLASSIFICATION:
        return OLD_CLASSIFICATION_INDICATOR
    return COICOP_2018_INDICATOR


def _download(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "polish-bonds-data inflation updater"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


if __name__ == "__main__":
    sys.exit(main())
