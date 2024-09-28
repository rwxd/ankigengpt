import re

from bs4 import BeautifulSoup


def sanitize_string(input: str) -> str:
    return re.sub(r"[^A-Za-z0-9-_\s]+", "", input)


def get_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = "\n".join(chunk for chunk in chunks if chunk)

    return text
