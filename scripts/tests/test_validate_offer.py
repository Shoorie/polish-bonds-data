import copy
import unittest
from pathlib import Path

from offer_file import read_offer
from validate_offer import problems_of

OCTOBER_2026 = read_offer(Path(__file__).resolve().parents[2] / "v1" / "offers" / "2026-10.json")


class ValidateOfferTest(unittest.TestCase):

    def test_october_offer_has_no_problems(self):
        self.assertEqual(problems_of(OCTOBER_2026), [])

    def test_offer_without_one_series_is_rejected(self):
        offer = copy.deepcopy(OCTOBER_2026)
        offer["series"] = offer["series"][1:]
        self.assertTrue(problems_of(offer))

    def test_family_bond_with_exchange_discount_is_rejected(self):
        offer = copy.deepcopy(OCTOBER_2026)
        rod = next(entry for entry in offer["series"] if entry["code"] == "ROD")
        rod["exchangePriceCents"] = 9_990
        self.assertEqual(problems_of(offer), ["ROD: family bonds are bought at the nominal price"])

    def test_rate_written_as_decimal_is_rejected(self):
        offer = copy.deepcopy(OCTOBER_2026)
        offer["referenceRateBasisPoints"] = 3.75
        self.assertEqual(problems_of(offer), ["referenceRateBasisPoints must be between 0 and 2000"])


if __name__ == "__main__":
    unittest.main()
