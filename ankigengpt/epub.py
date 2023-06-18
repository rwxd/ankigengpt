from dataclasses import dataclass
from pathlib import Path

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub


@dataclass
class Epub:
    title: str
    author: str
    content: list[str]


def parse_ebook(path: Path) -> Epub:
    book = epub.read_epub(str(path))
    content: list[str] = []
    author = book.get_metadata('DC', 'creator')
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    for item in items:
        # Chapters are typically located in epub documents items
        soup = BeautifulSoup(item.get_body_content().decode('utf-8'), 'html.parser')
        if item.is_chapter():
            pass

        text = [para.get_text().strip() for para in soup.find_all('p')]
        content.extend(text)

    return Epub(title=book.title or 'No title found', author=author, content=content)
