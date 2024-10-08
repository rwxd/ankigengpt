from pathlib import Path

import typer
from rich.console import Console

from ankigengpt.anki import DeckInput, generate_deck
from ankigengpt.epub import parse_ebook
from ankigengpt.gpt import _generate_cards_until_finish, calculate_tokens_of_text
from ankigengpt.kindle import extract_kindle_highlights
from ankigengpt.kobo import extract_kobo_highlights
from ankigengpt.logging import init_logger, logger
from ankigengpt.misc import get_text_from_html, sanitize_string
from ankigengpt.models import (
    EnumGPTModel,
    get_gpt_model,
    gpt_3_5_turbo,
    gpt_3_5_turbo_16k,
    gpt_4,
    gpt_4_32k,
)
from ankigengpt.templates import template_epub, template_kindle, template_plain
from ankigengpt.wallabag import WallabagConnector

app = typer.Typer()
console = Console()


@app.command()
def kindle_highlights(
    openai_token: str = typer.Option(..., envvar="OPENAI_TOKEN"),
    debug: bool = typer.Option(False),
    path: Path = typer.Option(..., help="Path to APA highlight notebook"),
    dest: Path = typer.Option(Path().cwd, help="Destination directory"),
    model: EnumGPTModel = typer.Option(
        EnumGPTModel.gpt_3_5_turbo.value, help="GPT model"
    ),
    include_source: bool = typer.Option(False, help="Include source of highlight"),
):
    init_logger(debug)
    resolved_model = get_gpt_model(model)
    highlights = extract_kindle_highlights(path)
    logger.info(f"Found {len(highlights.highlights)} highlights for {highlights.title}")
    cards = _generate_cards_until_finish(
        template_kindle,
        highlights.highlights,
        openai_token,
        cards_source=highlights.title,
        model=resolved_model,
    )
    input = DeckInput(highlights.title, cards)
    generate_deck(input, dest, include_source)


@app.command()
def plain(
    openai_token: str = typer.Option(..., envvar="OPENAI_TOKEN"),
    debug: bool = typer.Option(False),
    path: Path = typer.Option(..., help="Path to text file"),
    dest: Path = typer.Option(Path().cwd, help="Destination directory"),
    model: EnumGPTModel = typer.Option(
        EnumGPTModel.gpt_3_5_turbo.value, help="GPT model"
    ),
    include_source: bool = typer.Option(False, help="Include source of highlight"),
):
    init_logger(debug)
    resolved_model = get_gpt_model(model)
    with open(path) as f:
        raw = f.read()
        # remove markdown double new line
        raw = raw.replace("\n\n", "\n")
        content = raw.split("\n")
        cards = _generate_cards_until_finish(
            template_plain,
            content,
            openai_token,
            cards_source=path.name,
            model=resolved_model,
        )
    ankiInput = DeckInput(path.name, cards)
    generate_deck(ankiInput, dest, include_source)


@app.command()
def epub(
    openai_token: str = typer.Option(..., envvar="OPENAI_TOKEN"),
    debug: bool = typer.Option(False),
    path: Path = typer.Option(..., help="Path to epub file"),
    dest: Path = typer.Option(Path().cwd, help="Destination directory"),
    model: EnumGPTModel = typer.Option(
        EnumGPTModel.gpt_3_5_turbo.value, help="GPT model"
    ),
    include_source: bool = typer.Option(False, help="Include source of highlight"),
):
    init_logger(debug)
    resolved_model = get_gpt_model(model)
    book = parse_ebook(path)
    logger.info(f"{len(book.content)} items in book")
    logger.info(f'{len(" ".join(book.content))} chars')
    tokens = calculate_tokens_of_text(" ".join(book.content))
    logger.info(f"Book has {tokens} tokens")

    cards = _generate_cards_until_finish(
        template_epub,
        book.content,
        openai_token,
        cards_source=book.title,
        template_input={"title": book.title},
        model=resolved_model,
    )
    ankiInput = DeckInput(book.title, cards)
    generate_deck(ankiInput, dest, include_source)


@app.command()
def kobo_highlights(
    openai_token: str = typer.Option(..., envvar="OPENAI_TOKEN"),
    debug: bool = typer.Option(False),
    path: Path = typer.Option(..., help="Path to epub file"),
    dest: Path = typer.Option(Path().cwd, help="Destination directory"),
    model: EnumGPTModel = typer.Option(
        EnumGPTModel.gpt_3_5_turbo.value, help="GPT model"
    ),
    include_source: bool = typer.Option(False, help="Include source of highlight"),
):
    init_logger(debug)
    resolved_model = get_gpt_model(model)
    highlights = extract_kobo_highlights(path)
    logger.info(f"Found {len(highlights.highlights)} highlights for {highlights.title}")
    cards = _generate_cards_until_finish(
        template_kindle,
        highlights.highlights,
        openai_token,
        cards_source=highlights.title,
        model=resolved_model,
    )
    input = DeckInput(highlights.title, cards)
    generate_deck(input, dest, include_source)


@app.command()
def wallabag_article(
    openai_token: str = typer.Option(..., envvar="OPENAI_TOKEN"),
    debug: bool = typer.Option(False),
    dest: Path = typer.Option(Path().cwd, help="Destination directory"),
    model: EnumGPTModel = typer.Option(
        EnumGPTModel.gpt_3_5_turbo.value, help="GPT model"
    ),
    article_id: int = typer.Argument(help="Id of the wallabag article"),
    url=typer.Option(..., help="URL to wallabag instance", envvar="WALLABAG_URL"),
    user=typer.Option(
        ..., help="User on the wallabag instance", envvar="WALLABAG_USER"
    ),
    password=typer.Option(
        ..., help="Password on the wallabag instance", envvar="WALLABAG_PASSWORD"
    ),
    client_id=typer.Option(
        ..., help="Client id on the wallabag instance", envvar="WALLABAG_CLIENT_ID"
    ),
    client_secret=typer.Option(
        ...,
        help="Client secret on the wallabag instance",
        envvar="WALLABAG_CLIENT_SECRET",
    ),
    include_source: bool = typer.Option(False, help="Include source of highlight"),
):
    init_logger(debug)
    resolved_model = get_gpt_model(model)

    client = WallabagConnector(url, user, password, client_id, client_secret)
    entry = client.get_entry(article_id)
    logger.info(f'Found "{entry.title}"')
    content = get_text_from_html(entry.content)

    cards = _generate_cards_until_finish(
        template_kindle,
        content.split("\n"),
        openai_token,
        cards_source=entry.title,
        model=resolved_model,
    )
    input = DeckInput(sanitize_string(entry.title), cards)
    generate_deck(input, dest, include_source)


@app.command()
def list_models():
    for model in [gpt_3_5_turbo, gpt_3_5_turbo_16k, gpt_4, gpt_4_32k]:
        console.print(
            f"{model.name} - Max tokens: {model.max_tokens} - Price per token"
            + f" {model.price_per_token}"
        )
