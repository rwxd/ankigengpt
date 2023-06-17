import openai
from ankigengpt.logging import logger
import tiktoken


def prompt_openai(
    token: str,
    prompt: str,
    temperature=1.0,
    frequency_penalty=0.0,
    presence_penalty=1.0,
    model='gpt-3.5-turbo',
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
    logger.info(client.usage)
    return content


def calculate_tokens_of_text(text: str, model='gpt-3.5-turbo') -> int:
    enc = tiktoken.encoding_for_model(model)
    encoded = enc.encode(text)
    return len(encoded)
