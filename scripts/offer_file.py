import json
from pathlib import Path

from issue_letter import SeriesTerms

FORMAT_VERSION = 1

SERIES_TERMS_IN_YEARS = {
    "ROR": 1,
    "DOR": 2,
    "TOS": 3,
    "COI": 4,
    "EDO": 10,
    "ROS": 6,
    "ROD": 12,
}


def offer_of(month: str, reference_rate_basis_points: int, series: list[SeriesTerms]) -> dict:
    return {
        "formatVersion": FORMAT_VERSION,
        "month": month,
        "referenceRateBasisPoints": reference_rate_basis_points,
        "series": [_series_entry(terms) for terms in sorted(series, key=_series_order)],
    }


def write_offer(offer: dict, folder: Path) -> None:
    (folder / "offer.json").write_text(_content_of(offer), encoding="utf-8")
    write_monthly_offer(offer, folder)


def write_monthly_offer(offer: dict, folder: Path) -> None:
    (folder / "offers" / f"{offer['month']}.json").write_text(_content_of(offer), encoding="utf-8")
    _write_offer_months(folder)


def read_offer(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_offer_months(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_offer_months(folder: Path) -> None:
    months = sorted(path.stem for path in (folder / "offers").glob("*.json"))
    offer_months = {"formatVersion": FORMAT_VERSION, "months": months}
    (folder / "offer-months.json").write_text(_content_of(offer_months), encoding="utf-8")


def _content_of(document: dict) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def _series_order(terms: SeriesTerms) -> int:
    return list(SERIES_TERMS_IN_YEARS).index(terms.code)


def _series_entry(terms: SeriesTerms) -> dict:
    return {
        "code": terms.code,
        "issueCode": terms.issue_code,
        "termYears": SERIES_TERMS_IN_YEARS[terms.code],
        "firstPeriodRateBasisPoints": terms.first_period_rate_basis_points,
        "marginBasisPoints": terms.margin_basis_points,
        "earlyRedemptionFeeCents": terms.early_redemption_fee_cents,
        "exchangePriceCents": terms.exchange_price_cents,
    }
