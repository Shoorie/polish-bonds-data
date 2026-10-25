import re
from dataclasses import dataclass

POLISH_MONTHS = {
    "stycznia": 1,
    "lutego": 2,
    "marca": 3,
    "kwietnia": 4,
    "maja": 5,
    "czerwca": 6,
    "lipca": 7,
    "sierpnia": 8,
    "września": 9,
    "października": 10,
    "listopada": 11,
    "grudnia": 12,
}

NOMINAL_PRICE_CENTS = 10_000


@dataclass(frozen=True)
class SeriesTerms:
    code: str
    issue_code: str
    month: str
    first_period_rate_basis_points: int
    margin_basis_points: int
    early_redemption_fee_cents: int
    exchange_price_cents: int


def read_series_terms(code: str, letter_text: str) -> SeriesTerms:
    text = _joined_lines(letter_text)
    return SeriesTerms(
        code=code,
        issue_code=_issue_code(code, text),
        month=_sale_month(text),
        first_period_rate_basis_points=_first_period_rate(text),
        margin_basis_points=_margin(text),
        early_redemption_fee_cents=_early_redemption_fee(text),
        exchange_price_cents=_exchange_price(text),
    )


def _joined_lines(letter_text: str) -> str:
    return re.sub(r"\s+", " ", letter_text)


def _issue_code(code: str, text: str) -> str:
    return _required(rf"\b({code}\d{{4}}), zwane", text, "issue code")


def _sale_month(text: str) -> str:
    match = re.search(r"w dniach od \d+ do (?:dnia )?(?:\d+ )+([a-ząćęłńóśźż]+) (\d{4})", text)
    if not match:
        raise ValueError("sale period not found")
    month = POLISH_MONTHS[match.group(1)]
    return f"{match.group(2)}-{month:02d}"


def _first_period_rate(text: str) -> int:
    first_period = re.search(r"pierwszym okresie odsetkowym stopa procentowa wynos\w* (\d+,\d{2})%", text)
    fixed_for_whole_term = re.search(r"Oprocentowanie obligacji wynosi (\d+,\d{2})%", text)
    match = first_period or fixed_for_whole_term
    if not match:
        raise ValueError("first period rate not found")
    return _basis_points(match.group(1))


def _margin(text: str) -> int:
    later_periods = re.search(r"stał\w* marż\w* w wysokości (\d+,\d{2})%", text)
    any_period = re.search(r"marż\w* w wysokości (\d+,\d{2})%", text)
    match = later_periods or any_period
    return _basis_points(match.group(1)) if match else 0


def _early_redemption_fee(text: str) -> int:
    return _cents(_required(r"nie wyższą niż (\d+(?:,\d{2})?) zł", text, "early redemption fee"))


def _exchange_price(text: str) -> int:
    match = re.search(r"Cena zamiany jednej obligacji wynosi (\d+,\d{2}) zł", text)
    return _cents(match.group(1)) if match else NOMINAL_PRICE_CENTS


def _required(pattern: str, text: str, what: str) -> str:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"{what} not found")
    return match.group(1)


def _basis_points(percent: str) -> int:
    whole, hundredths = percent.split(",")
    return int(whole) * 100 + int(hundredths)


def _cents(amount: str) -> int:
    whole, _, hundredths = amount.partition(",")
    return int(whole) * 100 + int(hundredths or 0)
