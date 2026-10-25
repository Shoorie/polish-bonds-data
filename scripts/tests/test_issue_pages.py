import unittest
from pathlib import Path

from issue_pages import IssuePage, letter_link, other_documents, read_issue_pages

SITE = Path(__file__).resolve().parent / "site"
LISTING = (SITE / "listing.html").read_text(encoding="utf-8")
ISSUE_WITH_AMENDMENT = (SITE / "issue-ror0623.html").read_text(encoding="utf-8")


class IssuePagesTest(unittest.TestCase):

    def test_listing_gives_the_address_of_each_issue_of_the_wanted_series(self):
        self.assertEqual(
            read_issue_pages(LISTING, {"EDO", "ROD"}),
            [
                IssuePage(issue_code="ROD1038", path="/listy-emisyjne/?id=rod1038"),
                IssuePage(issue_code="EDO1028", path="/listy-emisyjne/?id=edo01028"),
            ],
        )

    def test_issue_page_gives_the_letter_and_not_the_amendment(self):
        self.assertEqual(letter_link(ISSUE_WITH_AMENDMENT), "/media_files/2d17acfd-e866-4097-83b1-a4a98ee403d4.pdf")

    def test_issue_page_lists_the_amendment_as_another_document(self):
        self.assertEqual(other_documents(ISSUE_WITH_AMENDMENT), ["/media_files/053d7661-0914-46f4-bd6d-1af754dd10a2.pdf"])


if __name__ == "__main__":
    unittest.main()
