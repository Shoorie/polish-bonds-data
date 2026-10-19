import json
from dataclasses import dataclass
from decimal import Decimal

FIRST_MONTH_PERIOD = 247
LAST_MONTH_PERIOD = 258
SAME_MONTH_LAST_YEAR = 5
NOT_PUBLISHED_FLAGS = {29, 30, 31, 306, 307, 308, 629}
PREVIOUS_YEAR_IS_100 = Decimal(100)


@dataclass(frozen=True)
class MonthlyInflation:
    month: str
    year_on_year_basis_points: int


def read_monthly_inflation(indicator_data: bytes) -> list[MonthlyInflation]:
    rows = json.loads(indicator_data, parse_float=Decimal)
    published = [row for row in rows if _is_published_month(row)]
    return sorted((_monthly_inflation(row) for row in published), key=lambda inflation: inflation.month)


def _is_published_month(row: dict) -> bool:
    return (
        FIRST_MONTH_PERIOD <= row["id-okres"] <= LAST_MONTH_PERIOD
        and row["id-sposob-prezentacji-miara"] == SAME_MONTH_LAST_YEAR
        and row["id-flaga"] not in NOT_PUBLISHED_FLAGS
    )


def _monthly_inflation(row: dict) -> MonthlyInflation:
    month = row["id-okres"] - FIRST_MONTH_PERIOD + 1
    return MonthlyInflation(
        month=f"{row['id-daty']}-{month:02d}",
        year_on_year_basis_points=_basis_points_above_previous_year(row["wartosc"]),
    )


def _basis_points_above_previous_year(index: Decimal) -> int:
    basis_points = (index - PREVIOUS_YEAR_IS_100) * 100
    if basis_points != basis_points.to_integral_value():
        raise ValueError(f"index {index} is more precise than a basis point")
    return int(basis_points)
