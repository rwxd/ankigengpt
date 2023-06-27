import random
from dataclasses import dataclass
from pathlib import Path

import genanki
import yaml


@dataclass
class AnkiCard:
    front: str
    back: str
    source: str


@dataclass
class DeckInput:
    name: str
    cards: list[AnkiCard]


def split_gpt_answer(answer: str) -> list[str]:
    '''Splits list into dicts'''
    splitted = []
    for pair in answer.split('\n-'):
        splitted.append(
            '\n'.join([i.replace('-', '').strip() for i in pair.split('\n')])
        )
    return splitted


def gpt_answer_to_cards(answer: str, source: str) -> AnkiCard:
    data = yaml.safe_load(answer)
    return AnkiCard(data['question'], data['answer'], source)


def generate_deck(input: DeckInput, dest: Path) -> None:
    my_deck = genanki.Deck(
        deck_id=random.randrange(11111111, 99999999, 8), name=input.name
    )

    for card in input.cards:
        my_note = genanki.Note(
            model=anki_model, fields=[card.front, card.back, 'Source: ' + card.source]
        )
        my_deck.add_note(my_note)

    package = genanki.Package(my_deck)

    package.write_to_file(dest.joinpath(input.name + '.apkg'))


anki_model = genanki.Model(
    model_id=9876543210,  # Unique ID for the model
    name='Basic Model',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Source'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '<div class="front-back">{{Front}}</div>',
            'afmt': '<div class="front-back">{{Front}}</div><br><div class="front-back">{{Back}}</div><br><div class="source">{{Source}}</div>',  # noqa
        },
    ],
    css='''
        .source {
            font-size: 0.5em;
            margin-top: 20px;
            text-align: center;
        }
        .front-back {
            font-size: 1.3em;
            margin-top: 20px;
            text-align: center;
        }
    ''',
)
