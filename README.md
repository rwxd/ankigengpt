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

## Kobo Highlights

You can activate the exporting of highlights on a kobo device by connecting it with USB and editing the file `.kobo/Kobo/Kobo eReader.conf` and adding this under `[FeatureSettings]`

```ini
[FeatureSettings]
ExportHighlights=true
```

After that on the kobo device it is possible to export highlights from a book.

Then you can get the files via USB and use the `kobo-highlights` command to create anki cards.

```bash
ankigengpt kobo-highlights --path ~/Downloads/BookHighlights.csv
```

## Plain text

Use a plain text file like markdown or txt

```bash
ankigengpt plain --debug --path ~/Downloads/book.md
```
