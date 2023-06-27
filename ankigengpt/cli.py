from pathlib import Path

import typer

from ankigengpt.anki import DeckInput, generate_deck
from ankigengpt.epub import parse_ebook
from ankigengpt.gpt import _generate_cards_until_finish, calculate_tokens_of_text
from ankigengpt.kindle import extract_kindle_highlights
from ankigengpt.logging import init_logger, logger
from ankigengpt.templates import template_epub, template_kindle, template_plain

app = typer.Typer()


@app.command()
def kindle_highlights(
    openai_token: str = typer.Option(..., envvar='OPENAI_TOKEN'),
    debug: bool = typer.Option(False),
    path: Path = typer.Option(..., help='Path to APA highlight notebook'),
    dest: Path = typer.Option(Path().cwd, help='Destination directory'),
):
    init_logger(debug)
    highlights = extract_kindle_highlights(path)
    logger.info(f'Found {len(highlights.highlights)} highlights for {highlights.title}')
    cards = _generate_cards_until_finish(
        template_kindle,
        highlights.highlights,
        openai_token,
        cards_source=highlights.title,
    )
    input = DeckInput(highlights.title, cards)
    generate_deck(input, dest)


@app.command()
def plain(
    openai_token: str = typer.Option(..., envvar='OPENAI_TOKEN'),
    debug: bool = typer.Option(False),
    path: Path = typer.Option(..., help='Path to text file'),
    dest: Path = typer.Option(Path().cwd, help='Destination directory'),
):
    init_logger(debug)
    with open(path) as f:
        raw = f.read()
        # remove markdown double new line
        raw = raw.replace('\n\n', '\n')
        content = raw.split('\n')
        cards = _generate_cards_until_finish(
            template_plain, content, openai_token, cards_source=path.name
        )
    ankiInput = DeckInput(path.name, cards)
    generate_deck(ankiInput, dest)


@app.command()
def epub(
    openai_token: str = typer.Option(..., envvar='OPENAI_TOKEN'),
    debug: bool = typer.Option(False),
    path: Path = typer.Option(..., help='Path to epub file'),
    dest: Path = typer.Option(Path().cwd, help='Destination directory'),
):
    init_logger(debug)
    book = parse_ebook(path)
    logger.info(f'{len(book.content)} items in book')
    logger.info(f'{len(" ".join(book.content))} chars')
    tokens = calculate_tokens_of_text(' '.join(book.content))
    logger.info(f'Book has {tokens} tokens')

    cards = _generate_cards_until_finish(
        template_epub,
        book.content,
        openai_token,
        cards_source=book.title,
        template_input={'title': book.title},
    )
    ankiInput = DeckInput(book.title, cards)
    generate_deck(ankiInput, dest)
