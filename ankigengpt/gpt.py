import openai
import tiktoken
from jinja2 import Template
from ratelimit import limits, sleep_and_retry
from rich.progress import Progress

from ankigengpt.anki import AnkiCard, gpt_answer_to_cards, split_gpt_answer
from ankigengpt.logging import logger

ONE_MINUTE = 60


@sleep_and_retry
@limits(3, period=ONE_MINUTE)
def prompt_openai(
    token: str,
    prompt: str,
    temperature=1.0,
    frequency_penalty=0.0,
    presence_penalty=1.0,
    # model='gpt-3.5-turbo',
    model='gpt-3.5-turbo-0613',
) -> str:
    openai.api_key = token
    client = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'user', 'content': prompt},
        ],
        # What sampling temperature to use, between 0 and 2.
        # Higher values like 0.8 will make the output more random,
        # while lower values like 0.2 will make it more focused and deterministic.
        temperature=temperature,
        # Number between -2.0 and 2.0.
        # Positive values penalize new tokens based on their existing frequency in the text so far,
        # decreasing the model's likelihood to repeat the same line verbatim.
        frequency_penalty=frequency_penalty,
        # Number between -2.0 and 2.0. Positive values penalize new tokens based on
        # whether they appear in the text so far, increasing the model's
        # likelihood to talk about new topics.
        presence_penalty=presence_penalty,
    )
    content = client.choices[0].message.content
    logger.info(f'GPT answered with with {len(content.split(" "))} words')
    logger.debug(client.usage)
    return content


def calculate_tokens_of_text(text: str, model='gpt-3.5-turbo') -> int:
    enc = tiktoken.encoding_for_model(model)
    encoded = enc.encode(text)
    return len(encoded)


def _generate_cards_until_finish(
    template: Template,
    inputs: list[str],
    openai_token: str,
    cards_source: str,
    token_limit=4000,
    template_input: dict = dict(),
) -> list[AnkiCard]:
    '''
    The function slices inputs into chunks less than a predefined token limit.
    It then renders the template and converts the output to Anki cards.
    '''
    intro = template.render(**template_input)

    tokens_intro = calculate_tokens_of_text(intro)
    logger.info(f'Prompt introduction tokens: {tokens_intro}')

    used_tokens = tokens_intro
    prompt = intro

    number_of_inputs = len(inputs)
    cards = []
    with Progress() as progress:
        task = progress.add_task('Prompting GPT...', total=number_of_inputs)
        for index, item in enumerate(inputs):
            item = f'{item}\n'
            input_tokens = calculate_tokens_of_text(item)

            # Add some space for the gpt answer
            needed_tokens = int(input_tokens + (input_tokens / 2))

            # Check if adding more tokens will exceed the limit or it is the last item
            if (used_tokens + needed_tokens >= token_limit) or (
                index + 1 == number_of_inputs
            ):
                logger.info(f'Token limit of {token_limit} reached for current prompt')

                # Get response from GPT
                try:
                    gpt_answer = prompt_openai(openai_token, prompt)
                    splitted_answer = split_gpt_answer(str(gpt_answer))
                    for item in splitted_answer:
                        try:
                            cards.append(gpt_answer_to_cards(item, cards_source))
                        except Exception as e:
                            logger.error(item)
                            logger.error(e)
                except Exception as e:
                    logger.error(e)

                # Reset the prompt and used tokens
                prompt = intro + item
                used_tokens = tokens_intro
            else:
                prompt += item
                used_tokens += needed_tokens

            progress.update(task, advance=1)

    logger.debug(f'{len(cards)} cards generated')
    return cards
