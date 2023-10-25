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


def generate_deck(input: DeckInput, dest: Path, source: bool = False) -> None:
    my_deck = genanki.Deck(
        deck_id=random.randrange(11111111, 99999999, 8), name=input.name
    )

    for card in input.cards:
        fields = [card.front, card.back]
        if source:
            fields.append('Source: ' + card.source)
        model = get_anki_model(source)
        my_note = genanki.Note(model=model, fields=fields)
        my_deck.add_note(my_note)

    package = genanki.Package(my_deck)

    package.write_to_file(dest.joinpath(input.name + '.apkg'))


def get_anki_model(source: bool = False) -> genanki.Model:
    fields = [
        {'name': 'Front'},
        {'name': 'Back'},
    ]
    if source:
        fields.append({'name': 'Source'})

    templates = [
        {
            'name': 'Card 1',
            'qfmt': '<div class="front-back">{{Front}}</div>',
            'afmt': '<div class="front-back">{{Front}}</div><br><div class="front-back">{{Back}}</div>',  # noqa
        },
    ]

    if source:
        templates[0]['afmt'] += '<br><div class="source">{{Source}}</div>'

    css = '''
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
    '''
    return genanki.Model(
        model_id=9876543210,  # Unique ID for the model
        name='AnkiGenGPT Basic Model',
        fields=fields,
        templates=templates,
        css=css,
    )
