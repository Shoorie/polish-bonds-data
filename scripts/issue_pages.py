import re
from dataclasses import dataclass


@dataclass(frozen=True)
class IssuePage:
    issue_code: str
    path: str


def read_issue_pages(listing_html: str, codes: set[str]) -> list[IssuePage]:
    options = re.findall(r'value="(/[a-z-]+/)\?id=([a-z0-9]+),[a-z]+"\s*data-id="[a-z]+">\s*([A-Z]{3}\d{4})', listing_html)
    return [
        IssuePage(issue_code=issue_code, path=f"{section}?id={site_id}")
        for section, site_id, issue_code in options
        if issue_code[:3] in codes
    ]


def letter_link(issue_html: str) -> str:
    links = re.findall(r'href="(/media_files/[^"]+\.pdf)"[^>]*>\s*(?:<[^>]+>\s*)*Pobierz list emisyjny', issue_html)
    if len(links) != 1:
        raise ValueError(f"expected one issue letter link, found {len(links)}")
    return links[0]


def other_documents(issue_html: str) -> list[str]:
    letter = letter_link(issue_html)
    return sorted(set(re.findall(r'/media_files/[^"\']+\.pdf', issue_html)) - {letter})
