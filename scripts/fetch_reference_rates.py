import sys
import urllib.request
from pathlib import Path

from bis_policy_rate import read_rate_changes
from nbp_reference_rate import read_current_reference_rate
from reference_rate import changes_in_force_since, with_latest_decision
from reference_rates_file import read_reference_rates, reference_rates_of, write_reference_rates

BIS_DAILY_POLICY_RATE = "https://stats.bis.org/api/v1/data/WS_CBPOL/D.PL?format=csv&startPeriod=2015-01-01"
NBP_RATES = "https://static.nbp.pl/dane/stopy/stopy_procentowe.xml"
FIRST_DAY = "2016-11-01"
RATES_FOLDER = Path(__file__).resolve().parent.parent / "v1"


def main() -> int:
    history = changes_in_force_since(read_rate_changes(_download(BIS_DAILY_POLICY_RATE)), FIRST_DAY)
    changes = with_latest_decision(history, read_current_reference_rate(_download(NBP_RATES)))
    reference_rates = reference_rates_of(changes)
    if reference_rates == _current_reference_rates():
        print("Reference rates unchanged")
        return 0

    write_reference_rates(reference_rates, RATES_FOLDER)
    print(f"Reference rates updated to {changes[-1].effective_from}")
    return 0


def _current_reference_rates() -> dict | None:
    current = RATES_FOLDER / "reference-rates.json"
    return read_reference_rates(current) if current.exists() else None


def _download(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "polish-bonds-data reference rate updater"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8-sig")


if __name__ == "__main__":
    sys.exit(main())
