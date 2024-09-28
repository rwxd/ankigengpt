# AnkiGenGPT

AnkiGenGPT is a Python CLI tool that harnesses the power of OpenAI's GPT-3 or GPT-4 model to transform your text into flashcards for Anki, an open-source spaced repetition software.

## Install

You can install AnkiGenGPT using pip:

```bash
pip3 -U install ankigengpt
```

Alternatively, you can use pipx for installation:

```bash
pipx install ankigengpt
```

## Configuration

To use AnkiGenGPT, you need an OpenAI API token, which can be provided either through the --openai-token command-line option or via the OPENAI_TOKEN environment variable.

## Epub

AnkiGenGPT can scan an epub file for text and use ChatGPT to create Anki cards. Here's an example of how to use it:

```bash
ankigengpt epub --path ~/Downloads/my-ebook.epub
```

## Kindle Highlights

To generate Anki cards from Kindle highlights, ensure the highlights are in the APA format, and then run the following command:

```bash
ankigengpt kindle-highlights --path ~/Downloads/Notebook.html
```

## Kobo Highlights

For Kobo highlights, you can enable the export feature on your Kobo device by connecting it via USB and modifying the .kobo/Kobo/Kobo eReader.conf file. Add the following under [FeatureSettings]:

```ini
[FeatureSettings]
ExportHighlights=true
```

After enabling export highlights on the Kobo device, you can retrieve the highlight files via USB and use the kobo-highlights command to create Anki cards:

```bash
ankigengpt kobo-highlights --path ~/Downloads/BookHighlights.csv
```

## Wallabag Article

```bash
export WALLABAG_URL="https://wallabag.com/"
export WALLABAG_USER=""
export WALLABAG_PASSWORD=""
export WALLABAG_CLIENT_ID=""
export WALLABAG_CLIENT_SECRET=""

ankigengpt wallabag-article 1844
```

## Plain text

ou can also use AnkiGenGPT with plain text files such as markdown or txt. Here's how to use it:

```bash
ankigengpt plain --path ~/Downloads/book.md
```

## Debugging

To debug AnkiGenGPT, you can use the --debug option.
