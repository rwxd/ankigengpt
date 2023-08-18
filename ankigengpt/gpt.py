import openai
import tiktoken
from jinja2 import Template
from rich.progress import Progress

from ankigengpt.anki import AnkiCard, gpt_answer_to_cards, split_gpt_answer
from ankigengpt.logging import logger
from ankigengpt.models import GPTModel, gpt_3_5_turbo

ONE_MINUTE = 60


# @sleep_and_retry
# @limits(10, period=ONE_MINUTE)
def prompt_openai(
    token: str,
    prompt: str,
    temperature=1.0,
    frequency_penalty=0.0,
    presence_penalty=1.0,
    model: GPTModel = gpt_3_5_turbo,
) -> str:
    openai.api_key = token
    client = openai.ChatCompletion.create(
        model=model.name,
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
    model: GPTModel = gpt_3_5_turbo,
    template_input: dict = dict(),
) -> list[AnkiCard]:
    '''
    The function slices inputs into chunks less than a predefined token limit.
    It then renders the template and converts the output to Anki cards.
    '''
    intro = template.render(**template_input)

    tokens_intro = calculate_tokens_of_text(intro)
    logger.info(f'Prompt introduction tokens: {tokens_intro}')

    tokens_all = sum([calculate_tokens_of_text(item) for item in inputs])
    cost_tokens_all = model.calculate_price(tokens_all)
    logger.info(f'Estimated cost: {cost_tokens_all}$')

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
            needed_tokens = int(input_tokens + (input_tokens / 6))

            # Check if adding more tokens will exceed the limit or it is the last item
            if (used_tokens + needed_tokens >= model.max_tokens) or (
                index + 1 == number_of_inputs
            ):
                logger.info(
                    f'Token limit of {model.max_tokens} reached for current prompt'
                )

                # Get response from GPT
                try:
                    gpt_answer = prompt_openai(openai_token, prompt, model=model)
                    splitted_answer = split_gpt_answer(str(gpt_answer))
                    logger.info(f'Splitted answer into {len(splitted_answer)} parts')
                    for item in splitted_answer:
                        try:
                            cards.append(gpt_answer_to_cards(item, cards_source))
                        except Exception as e:
                            logger.error(f'Error: {e} for item: {item}')
                            logger.debug(gpt_answer)
                            logger.debug(splitted_answer)
                except Exception as e:
                    logger.error(e)

                # Reset the prompt and used tokens
                prompt = intro + item
                used_tokens = tokens_intro
            else:
                prompt += item
                used_tokens += needed_tokens

            progress.update(task, advance=1)

    logger.info(f'{len(cards)} cards generated')
    return cards


def get_available_models(token: str) -> list[str]:
    models = openai.Model.list(api_key=token)
    print(models)
    if models:
        return [model['id'] for model in models['data']]
    return []
