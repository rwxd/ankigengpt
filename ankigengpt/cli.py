import typer
from pathlib import Path
from ankigengpt.logging import init_logger, logger
from ankigengpt.kindle import extract_kindle_highlights
from ankigengpt.templates import template_kindle
from ankigengpt.gpt import prompt_openai, calculate_tokens_of_text
from ankigengpt.anki import AnkiCard, generate_deck, gpt_answer_to_cards, DeckInput
from jinja2 import Template

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
    cards = generate_cards_until_finish(
        template_kindle, highlights.highlights, openai_token
    )
    input = DeckInput(highlights.title, cards)
    generate_deck(input, dest)


@app.command()
def epub(
    openai_token: str = typer.Option(..., envvar='OPENAI_TOKEN'),
    debug: bool = typer.Option(False),
    path: Path = typer.Option(..., help='Path to APA highlight notebook'),
    dest: Path = typer.Option(
        Path('output.apkg'), help='Destination file for the anki cards'
    ),
):
    pass


def generate_cards_until_finish(
    template: Template,
    inputs: list[str],
    openai_token: str,
    token_limit=4000,
) -> list[AnkiCard]:
    '''
    Slices input into chunks that are less than a defined limit of tokens.
    Renders the template and converts the output to anki cards.
    '''
    intro = template.render()
    # tokens gpt needs for the cards of one input
    default_answer_tokens = 50

    tokens_intro = calculate_tokens_of_text(intro)
    logger.info(f'Prompt introduction tokens: {tokens_intro}')

    used_tokens = tokens_intro
    prompt = intro

    number_of_inputs = len(inputs)
    cards = []
    for index, item in enumerate(inputs):
        item = f'Text: {item}\n\n'
        input_tokens = calculate_tokens_of_text(item)
        needed_tokens = input_tokens + default_answer_tokens
        if used_tokens + needed_tokens <= token_limit:
            logger.debug(f'Adding to prompt: "{item}"')
            prompt = prompt + item

            # not the end, add more text to the prompt
            if index + 1 != number_of_inputs:
                continue
        else:
            logger.info(f'Token limit of {token_limit} reached for current prompt')

        logger.info(f'Prompting gpt')
        gpt_answer = prompt_openai(openai_token, prompt)
        cards.extend(gpt_answer_to_cards(gpt_answer))
        prompt = intro + item
        logger.debug(f'{len(cards)} number of cards')

    return cards
