import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

from issue_letter import SeriesTerms, read_series_terms
from issue_pages import IssuePage, letter_link, other_documents, read_issue_pages
from offer_file import SERIES_TERMS_IN_YEARS, offer_of, read_offer, write_monthly_offer
from pdf_text import text_of
from reference_rate import rate_on
from reference_rates_file import changes_of, read_reference_rates

SITE = "https://www.obligacjeskarbowe.pl"
LISTINGS = ["/listy-emisyjne/", "/archiwum-listow-emisyjnych/"]
FIRST_MONTH = "2016-11"
PAUSE_BETWEEN_REQUESTS_SECONDS = 0.7
OFFER_FOLDER = Path(__file__).resolve().parent.parent / "v1"


def main() -> int:
    last_month = read_offer(OFFER_FOLDER / "offer.json")["month"]
    pages = [page for page in _issue_pages() if FIRST_MONTH <= _sale_month_of(page.issue_code) < last_month]
    series_by_month = defaultdict(list)
    for number, page in enumerate(sorted(pages, key=lambda page: page.issue_code), start=1):
        terms = _terms_of(page)
        series_by_month[terms.month].append(terms)
        print(f"{number}/{len(pages)} {terms.issue_code} {terms.month}", flush=True)

    changes = changes_of(read_reference_rates(OFFER_FOLDER / "reference-rates.json"))
    for month, series in sorted(series_by_month.items()):
        write_monthly_offer(offer_of(month, rate_on(changes, f"{month}-01"), series), OFFER_FOLDER)
    print(f"Wrote {len(series_by_month)} months from {min(series_by_month)} to {max(series_by_month)}")
    return 0


def _issue_pages() -> list[IssuePage]:
    pages = []
    for listing in LISTINGS:
        pages += read_issue_pages(_download(SITE + listing).decode("utf-8"), set(SERIES_TERMS_IN_YEARS))
    return pages


def _sale_month_of(issue_code: str) -> str:
    maturity = (2000 + int(issue_code[5:7])) * 12 + int(issue_code[3:5]) - 1
    sale = maturity - SERIES_TERMS_IN_YEARS[issue_code[:3]] * 12
    return f"{sale // 12}-{sale % 12 + 1:02d}"


def _terms_of(page: IssuePage) -> SeriesTerms:
    issue_html = _download(SITE + page.path).decode("utf-8")
    for document in other_documents(issue_html):
        print(f"{page.issue_code}: check {SITE}{document}, it may amend the letter", flush=True)
    terms = read_series_terms(page.issue_code[:3], text_of(_download(SITE + letter_link(issue_html))))
    if terms.issue_code != page.issue_code or terms.month != _sale_month_of(page.issue_code):
        raise ValueError(f"{page.path} holds the letter of {terms.issue_code} sold in {terms.month}")
    return terms


def _download(url: str) -> bytes:
    time.sleep(PAUSE_BETWEEN_REQUESTS_SECONDS)
    request = urllib.request.Request(url, headers={"User-Agent": "polish-bonds-data offer archive"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


if __name__ == "__main__":
    sys.exit(main())
