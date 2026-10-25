import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_offer_archive import problems_of_archive

PUBLISHED = Path(__file__).resolve().parents[2] / "v1"


class ValidateOfferArchiveTest(unittest.TestCase):

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        shutil.copytree(PUBLISHED, self.folder, dirs_exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.folder)

    def test_published_archive_has_no_problems(self):
        self.assertEqual(problems_of_archive(self.folder), [])

    def test_missing_month_is_rejected(self):
        (self.folder / "offers" / "2020-01.json").unlink()
        self._edit("offer-months.json", lambda months: months["months"].remove("2020-01"))
        self.assertEqual(problems_of_archive(self.folder), ["offer-months.json: 2020-02 must come right after 2019-12"])

    def test_month_file_not_listed_is_rejected(self):
        self._edit("offer-months.json", lambda months: months["months"].pop())
        self.assertIn("offer-months.json must list exactly the months in offers/", problems_of_archive(self.folder))

    def test_reference_rate_other_than_on_the_first_day_is_rejected(self):
        self._edit("offers/2022-07.json", lambda offer: offer.update(referenceRateBasisPoints=650))
        self.assertEqual(
            problems_of_archive(self.folder),
            ["offers/2022-07.json: referenceRateBasisPoints must be 600, the rate on 2022-07-01"],
        )

    def test_current_offer_other_than_the_last_month_is_rejected(self):
        self._edit("offer.json", lambda offer: offer.update(referenceRateBasisPoints=0))
        self.assertIn("offer.json must be the same as offers/2026-10.json", problems_of_archive(self.folder))

    def _edit(self, name: str, change) -> None:
        path = self.folder / name
        document = json.loads(path.read_text(encoding="utf-8"))
        change(document)
        path.write_text(json.dumps(document), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
