import unittest
from pathlib import Path

from bis_policy_rate import read_rate_changes
from nbp_reference_rate import read_current_reference_rate
from reference_rate import RateChange, changes_in_force_since, rate_on, with_latest_decision

FIXTURES = Path(__file__).resolve().parent
BIS_RATES = (FIXTURES / "bis" / "policy-rate-pl.csv").read_text(encoding="utf-8")
NBP_RATES = (FIXTURES / "nbp" / "stopy_procentowe-2026-03-05.xml").read_text(encoding="utf-8-sig")
HISTORY = [
    RateChange(effective_from="2015-03-05", basis_points=150),
    RateChange(effective_from="2020-03-18", basis_points=100),
    RateChange(effective_from="2026-03-05", basis_points=375),
]


class ReferenceRateTest(unittest.TestCase):

    def test_bis_daily_rates_give_one_change_per_decision(self):
        self.assertEqual(
            read_rate_changes(BIS_RATES),
            [
                RateChange(effective_from="2015-01-02", basis_points=200),
                RateChange(effective_from="2015-03-05", basis_points=150),
                RateChange(effective_from="2020-03-18", basis_points=100),
                RateChange(effective_from="2026-03-05", basis_points=375),
            ],
        )

    def test_nbp_rates_give_the_current_reference_rate_with_its_date(self):
        self.assertEqual(read_current_reference_rate(NBP_RATES), RateChange(effective_from="2026-03-05", basis_points=375))

    def test_history_since_a_day_starts_with_the_rate_in_force_that_day(self):
        changes = changes_in_force_since(read_rate_changes(BIS_RATES), "2016-11-01")
        self.assertEqual(changes[0], RateChange(effective_from="2015-03-05", basis_points=150))

    def test_newer_nbp_decision_is_added_after_the_history(self):
        decision = RateChange(effective_from="2026-11-05", basis_points=350)
        self.assertEqual(with_latest_decision(HISTORY, decision), HISTORY + [decision])

    def test_nbp_decision_already_in_the_history_adds_nothing(self):
        self.assertEqual(with_latest_decision(HISTORY, HISTORY[-1]), HISTORY)

    def test_nbp_decision_contradicting_the_history_is_an_error(self):
        with self.assertRaises(ValueError):
            with_latest_decision(HISTORY, RateChange(effective_from="2026-03-05", basis_points=400))

    def test_rate_on_a_day_is_the_last_change_until_that_day(self):
        self.assertEqual(rate_on(HISTORY, "2020-03-17"), 150)
        self.assertEqual(rate_on(HISTORY, "2020-03-18"), 100)


if __name__ == "__main__":
    unittest.main()
