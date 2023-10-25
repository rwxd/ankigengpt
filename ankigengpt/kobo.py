from dataclasses import dataclass
from pathlib import Path

from ankigengpt.misc import sanitize_string


@dataclass
class KoboHighlights:
    title: str
    highlights: list[str]


def extract_kobo_highlights(path: Path) -> KoboHighlights:
    with open(path) as f:
        content = f.read()
    lines = content.split('\n')
    if len(lines) < 2:
        raise ValueError('File does not contain highlights')

    title = sanitize_string(lines[0])

    highlights = []
    for highlight in content.split('\n\n')[1:]:
        text = highlight.strip()
        highlights.append(text)

    return KoboHighlights(title, highlights)
