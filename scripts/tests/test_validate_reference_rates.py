import copy
import unittest
from pathlib import Path

from reference_rates_file import read_reference_rates
from validate_reference_rates import problems_of

REFERENCE_RATES = read_reference_rates(Path(__file__).resolve().parents[2] / "v1" / "reference-rates.json")


class ValidateReferenceRatesTest(unittest.TestCase):

    def test_published_reference_rates_have_no_problems(self):
        self.assertEqual(problems_of(REFERENCE_RATES), [])

    def test_changes_out_of_order_are_rejected(self):
        reference_rates = copy.deepcopy(REFERENCE_RATES)
        changes = reference_rates["changes"]
        changes[1], changes[2] = changes[2], changes[1]
        self.assertEqual(problems_of(reference_rates), [f"{changes[2]['effectiveFrom']} must come after {changes[1]['effectiveFrom']}"])

    def test_rate_written_as_decimal_is_rejected(self):
        reference_rates = copy.deepcopy(REFERENCE_RATES)
        reference_rates["changes"][0]["basisPoints"] = 1.5
        self.assertEqual(problems_of(reference_rates), ["2015-03-05: basisPoints must be between 0 and 2000"])

    def test_change_repeating_the_previous_rate_is_rejected(self):
        reference_rates = copy.deepcopy(REFERENCE_RATES)
        changes = reference_rates["changes"]
        changes[1]["basisPoints"] = changes[0]["basisPoints"]
        self.assertEqual(problems_of(reference_rates), [f"{changes[1]['effectiveFrom']} repeats the rate of 2015-03-05"])

    def test_history_starting_after_the_first_offer_is_rejected(self):
        reference_rates = copy.deepcopy(REFERENCE_RATES)
        reference_rates["changes"] = reference_rates["changes"][1:]
        self.assertEqual(problems_of(reference_rates), ["changes must start with the rate in force on 2016-11-01"])


if __name__ == "__main__":
    unittest.main()
