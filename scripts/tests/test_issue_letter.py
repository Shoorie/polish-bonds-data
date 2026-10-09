import unittest
from pathlib import Path

from issue_letter import SeriesTerms, read_series_terms

LETTERS = Path(__file__).resolve().parent / "letters"


def terms_of(code: str) -> SeriesTerms:
    text = (LETTERS / f"{code.lower()}-2026-10.txt").read_text(encoding="utf-8")
    return read_series_terms(code, text)


class IssueLetterTest(unittest.TestCase):

    def test_edo_letter_gives_first_year_rate_margin_fee_and_exchange_price(self):
        self.assertEqual(
            terms_of("EDO"),
            SeriesTerms(
                code="EDO",
                issue_code="EDO1036",
                month="2026-10",
                first_period_rate_basis_points=535,
                margin_basis_points=200,
                early_redemption_fee_cents=300,
                exchange_price_cents=9990,
            ),
        )

    def test_tos_letter_gives_fixed_rate_without_margin(self):
        tos = terms_of("TOS")
        self.assertEqual(tos.first_period_rate_basis_points, 440)
        self.assertEqual(tos.margin_basis_points, 0)

    def test_dor_letter_gives_margin_above_reference_rate(self):
        self.assertEqual(terms_of("DOR").margin_basis_points, 15)

    def test_family_letters_have_no_exchange_so_price_is_nominal(self):
        self.assertEqual(terms_of("ROS").exchange_price_cents, 10_000)
        self.assertEqual(terms_of("ROD").exchange_price_cents, 10_000)

    def test_every_letter_is_for_the_same_month(self):
        months = {terms_of(code).month for code in ["ROR", "DOR", "TOS", "COI", "EDO", "ROS", "ROD"]}
        self.assertEqual(months, {"2026-10"})


if __name__ == "__main__":
    unittest.main()
