import re

from reference_rate import RateChange


def read_current_reference_rate(rates_xml: str) -> RateChange:
    entry = re.search(r'<pozycja\s[^>]*id="ref"[^>]*>', rates_xml)
    if not entry:
        raise ValueError("NBP reference rate not found")
    rate = re.search(r'oprocentowanie="(\d+),(\d{2})"', entry.group(0))
    since = re.search(r'obowiazuje_od="(\d{4}-\d{2}-\d{2})"', entry.group(0))
    if not rate or not since:
        raise ValueError("NBP reference rate has no value or date")
    return RateChange(effective_from=since.group(1), basis_points=int(rate.group(1)) * 100 + int(rate.group(2)))
