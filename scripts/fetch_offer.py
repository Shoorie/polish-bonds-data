import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from issue_letter import read_series_terms
from nbp_reference_rate import read_current_reference_rate
from offer_file import offer_of, read_offer, write_offer

SITE = "https://www.obligacjeskarbowe.pl"
NBP_RATES = "https://static.nbp.pl/dane/stopy/stopy_procentowe.xml"
OFFER_FOLDER = Path(__file__).resolve().parent.parent / "v1"

SERIES_PAGES = {
    "ROR": "/oferta-obligacji/obligacje-roczne-ror/",
    "DOR": "/oferta-obligacji/obligacje-2-letnie-dor/",
    "TOS": "/oferta-obligacji/obligacje-3-letnie-tos/",
    "COI": "/oferta-obligacji/obligacje-4-letnie-coi/",
    "EDO": "/oferta-obligacji/obligacje-10-letnie-edo/",
    "ROS": "/oferta-obligacji/obligacje-6-letnie-ros/",
    "ROD": "/oferta-obligacji/obligacje-12-letnie-rod/",
}


def main() -> int:
    series = [read_series_terms(code, _issue_letter_text(page)) for code, page in SERIES_PAGES.items()]
    months = {terms.month for terms in series}
    if len(months) != 1:
        print(f"Issue letters cover different months: {sorted(months)}")
        return 1

    offer = offer_of(months.pop(), _reference_rate_basis_points(), series)
    if offer == _current_offer():
        print("Offer unchanged")
        return 0

    write_offer(offer, OFFER_FOLDER)
    print(f"Offer updated to {offer['month']}")
    return 0


def _current_offer() -> dict | None:
    current = OFFER_FOLDER / "offer.json"
    return read_offer(current) if current.exists() else None


def _issue_letter_text(series_page: str) -> str:
    page = _download(SITE + series_page).decode("utf-8")
    link = re.search(r'href="(/media_files/[^"]+\.pdf)"[^>]*>\s*Zobacz list emisyjny', page)
    if not link:
        raise ValueError(f"issue letter link not found on {series_page}")
    return _pdf_text(_download(SITE + link.group(1)))


def _reference_rate_basis_points() -> int:
    return read_current_reference_rate(_download(NBP_RATES).decode("utf-8-sig")).basis_points


def _pdf_text(pdf: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as file:
        file.write(pdf)
        file.flush()
        return subprocess.run(
            ["pdftotext", "-layout", file.name, "-"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout


def _download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "polish-bonds-data offer updater"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


if __name__ == "__main__":
    sys.exit(main())
