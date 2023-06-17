import re


def sanitize_string(input: str) -> str:
    return re.sub(r'[^A-Za-z0-9-_\s]+', '', input)
