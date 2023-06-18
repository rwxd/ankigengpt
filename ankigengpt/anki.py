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


def gpt_answer_to_cards(answer: str, source: str) -> list[AnkiCard]:
    data = yaml.safe_load(answer)
    return [AnkiCard(i['question'], i['answer'], source) for i in data]


def generate_deck(input: DeckInput, dest: Path) -> None:
    my_deck = genanki.Deck(
        deck_id=random.randrange(11111111, 99999999, 8), name=input.name
    )

    for card in input.cards:
        my_note = genanki.Note(
            model=anki_model, fields=[card.front, card.back, card.source]
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
            'qfmt': '{{Front}}',
            'afmt': '{{Front}}<br>{{Back}}<br>{{Source}}',
        },
    ],
)
