import json
from pathlib import Path

from gus_indicator import MonthlyInflation

FORMAT_VERSION = 1


def inflation_of(months: list[MonthlyInflation]) -> dict:
    return {
        "formatVersion": FORMAT_VERSION,
        "months": [_month_entry(inflation) for inflation in months],
    }


def write_inflation(inflation: dict, folder: Path) -> None:
    content = json.dumps(inflation, ensure_ascii=False, indent=2) + "\n"
    (folder / "inflation.json").write_text(content, encoding="utf-8")


def read_inflation(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _month_entry(inflation: MonthlyInflation) -> dict:
    return {
        "month": inflation.month,
        "yearOnYearBasisPoints": inflation.year_on_year_basis_points,
    }
