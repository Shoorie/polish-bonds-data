import csv
import io
from decimal import Decimal

from reference_rate import RateChange

NOT_OBSERVED = {"", "NaN"}


def read_rate_changes(daily_rates_csv: str) -> list[RateChange]:
    changes = []
    for row in csv.DictReader(io.StringIO(daily_rates_csv)):
        if row["OBS_VALUE"] in NOT_OBSERVED:
            continue
        basis_points = _basis_points(row["OBS_VALUE"])
        if not changes or changes[-1].basis_points != basis_points:
            changes.append(RateChange(effective_from=row["TIME_PERIOD"], basis_points=basis_points))
    return changes


def _basis_points(percent: str) -> int:
    basis_points = Decimal(percent) * 100
    if basis_points != basis_points.to_integral_value():
        raise ValueError(f"rate {percent} is more precise than a basis point")
    return int(basis_points)
