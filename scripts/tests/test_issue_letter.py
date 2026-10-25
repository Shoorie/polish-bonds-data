import unittest
from pathlib import Path

from issue_letter import SeriesTerms, read_series_terms

LETTERS = Path(__file__).resolve().parent / "letters"


def terms_of(code: str, month: str = "2026-10") -> SeriesTerms:
    text = (LETTERS / f"{code.lower()}-{month}.txt").read_text(encoding="utf-8")
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

    def test_older_letter_gives_the_fixed_margin_of_later_periods_not_the_first_period_one(self):
        self.assertEqual(
            terms_of("EDO", "2017-01"),
            SeriesTerms(
                code="EDO",
                issue_code="EDO0127",
                month="2017-01",
                first_period_rate_basis_points=270,
                margin_basis_points=150,
                early_redemption_fee_cents=200,
                exchange_price_cents=9990,
            ),
        )

    def test_letter_selling_until_a_day_of_the_month_gives_the_sale_month(self):
        self.assertEqual(terms_of("COI", "2024-01").month, "2024-01")

    def test_letter_with_two_last_days_of_sale_gives_the_sale_month(self):
        self.assertEqual(terms_of("EDO", "2018-07").month, "2018-07")

    def test_letter_with_a_cut_word_before_the_rate_gives_the_first_period_rate(self):
        self.assertEqual(terms_of("EDO", "2024-01").first_period_rate_basis_points, 690)

    def test_fee_in_whole_zloty_gives_the_fee_in_cents(self):
        self.assertEqual(terms_of("ROS", "2024-10").early_redemption_fee_cents, 200)

    def test_letter_with_an_exchange_promotion_gives_the_lower_exchange_price(self):
        self.assertEqual(terms_of("EDO", "2023-07").exchange_price_cents, 9940)


if __name__ == "__main__":
    unittest.main()
