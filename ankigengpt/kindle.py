from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup

from ankigengpt.misc import sanitize_string


@dataclass
class KindleHighlights:
    title: str
    author: str
    highlights: list[str]


def extract_kindle_highlights(path: Path) -> KindleHighlights:
    with open(path) as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
    title = sanitize_string(soup.find('div', class_='bookTitle').text.strip())
    author = sanitize_string(soup.find('div', class_='authors').text.strip())

    highlights = []
    notes = soup.find_all('div', class_='noteText')
    for item in notes:
        highlights.append(item.text.strip())
    return KindleHighlights(title, author, highlights)
