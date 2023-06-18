# AnkiGenGPT

This Python CLI tool leverages the power of OpenAI's GPT-3 or GPT-4 model to convert your text into flashcards for use in Anki, an open-source spaced repetition software.

## Install

```bash
pip3 -U install ankigengpt
```

or via pipx

```bash
pipx install ankigengpt
```

## Configuration

An openai api token is needed, it can be used with `--openai-token` or via the environment variable `OPENAI_TOKEN`.

## Epub

Scans an epub for text and asks chatgpt for anki cards.

```bash
ankigengpt epub --path ~/Downloads/my-ebook.epub
```

## Kindle Highlights

Uses the highlights to create anki cards.

> The kindle highlights are needed in the `APA` format.

```bash
ankigengpt kindle-highlights --path ~/Downloads/Notebook.html
```
