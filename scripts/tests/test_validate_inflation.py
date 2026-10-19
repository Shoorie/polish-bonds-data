import copy
import unittest
from pathlib import Path

from inflation_file import read_inflation
from validate_inflation import problems_of

INFLATION = read_inflation(Path(__file__).resolve().parents[2] / "v1" / "inflation.json")


class ValidateInflationTest(unittest.TestCase):

    def test_published_inflation_has_no_problems(self):
        self.assertEqual(problems_of(INFLATION), [])

    def test_missing_month_is_rejected(self):
        inflation = copy.deepcopy(INFLATION)
        del inflation["months"][5]
        self.assertEqual(problems_of(inflation), ["2010-07 must come right after 2010-05"])

    def test_inflation_written_as_decimal_is_rejected(self):
        inflation = copy.deepcopy(INFLATION)
        inflation["months"][0]["yearOnYearBasisPoints"] = 3.5
        self.assertEqual(problems_of(inflation), ["2010-01: yearOnYearBasisPoints must be between -1000 and 5000"])

    def test_history_starting_later_is_rejected(self):
        inflation = copy.deepcopy(INFLATION)
        inflation["months"] = inflation["months"][12:]
        self.assertEqual(problems_of(inflation), ["months must start at 2010-01"])


if __name__ == "__main__":
    unittest.main()
