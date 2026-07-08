# Quickstart

This page is a 60-second first run. If you want a full install walkthrough see
[Installation](installation.md); if you want a deep dive into the CLI see
[CLI](usage/cli.md); for the Python library see
[Python API](usage/library.md).

## 1. Install

```bash
pip install normadocs
```

You also need [Pandoc](https://pandoc.org/installing.html) on your `PATH`.
Quick check:

```bash
pandoc --version
```

## 2. Create a Markdown input

Save the following as `paper.md`:

```markdown
**The Effects of Reading on Concentration**

Jane Doe
Department of Psychology
2026-04-10

# Abstract

This paper reviews the literature on reading and attention.

**Keywords:** reading, attention, learning
```

## 3. Convert

APA 7th Edition (the default):

```bash
normadocs paper.md
```

ICONTEC NTC 1486 (Colombian / LATAM academic standard):

```bash
normadocs paper.md --style icontec
```

IEEE 8th Edition (engineering / technical):

```bash
normadocs paper.md --style ieee
```

The output appears in the current working directory as
`paper_APA.docx` (or `paper_ICONTEC.docx`, `paper_IEEE.docx`).

## 4. Add a bibliography (optional)

If you have a BibTeX file, pass it with `-b` and optionally a CSL style with
`-c`. See [Bibliography](bibliography.md) for details.

```bash
normadocs paper.md --style apa --bibliography references.bib --csl apa.csl
```

## 5. Generate a PDF (optional)

```bash
normadocs paper.md --style apa --format pdf
```

This requires either [LibreOffice](https://www.libreoffice.org/) (recommended)
or `pip install normadocs[pdf]` (WeasyPrint). See
[PDF Output](pdf-output.md).

## 6. Verify the output

```bash
ls -la paper_*.docx
```

Open the file in Word, LibreOffice, or any DOCX viewer. The cover page,
abstract, and headings should follow the chosen standard.

## Next steps

- [Examples](examples.md) — full sample documents for each standard.
- [CLI Reference](usage/cli.md) — every flag documented.
- [Standards](standards/index.md) — what each standard assumes.
- [Troubleshooting](troubleshooting.md) — common first-run issues.
