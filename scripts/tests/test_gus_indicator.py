import unittest
from pathlib import Path

from gus_indicator import MonthlyInflation, read_monthly_inflation

CPI_2026 = (Path(__file__).resolve().parent / "gus" / "cpi-2026.json").read_bytes()


def indicator_data_of(period: int, value: str, flag: int = 36) -> bytes:
    row = f'{{"id-okres": {period}, "id-sposob-prezentacji-miara": 5, "id-daty": 2026, "id-flaga": {flag}, "wartosc": {value}}}'
    return f"[{row}]".encode()


class GusIndicatorTest(unittest.TestCase):

    def test_published_year_gives_every_month_above_the_same_month_last_year(self):
        self.assertEqual(
            read_monthly_inflation(CPI_2026)[-3:],
            [
                MonthlyInflation(month="2026-07", year_on_year_basis_points=300),
                MonthlyInflation(month="2026-08", year_on_year_basis_points=340),
                MonthlyInflation(month="2026-09", year_on_year_basis_points=410),
            ],
        )

    def test_index_below_100_gives_negative_inflation(self):
        self.assertEqual(
            read_monthly_inflation(indicator_data_of(248, "98.40000")),
            [MonthlyInflation(month="2026-02", year_on_year_basis_points=-160)],
        )

    def test_preliminary_month_is_left_out(self):
        self.assertEqual(read_monthly_inflation(indicator_data_of(256, "104.30000", flag=31)), [])

    def test_quarter_is_left_out(self):
        self.assertEqual(read_monthly_inflation(indicator_data_of(270, "103.10000")), [])

    def test_index_more_precise_than_basis_point_is_rejected(self):
        with self.assertRaises(ValueError):
            read_monthly_inflation(indicator_data_of(247, "102.105"))


if __name__ == "__main__":
    unittest.main()
