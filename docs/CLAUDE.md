# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NormaDocs** is a professional open-source tool that converts Markdown documents to academic-standard DOCX/PDF formats (APA 7th Edition, ICONTEC NTC 1486). It provides automatic title pages, bibliography support (BibTeX/CSL), and applies formatting rules programmatically using python-docx.

## Common Commands

```bash
# Install development dependencies
make install

# Run tests
make test

# Run tests with coverage (minimum 60%)
make test-cov

# Lint: ruff check + ruff format check + mypy
make lint

# Format code
make format

# Security scan with Bandit
make security

# Run all quality checks (lint + test-cov + security)
make check

# Build package (wheel + sdist)
make build
```

**Requirements**: Pandoc must be installed on the system for conversion to work.

## Architecture

The project follows a **pipeline architecture** with three main stages:

1. **Preprocessor** ([preprocessor.py](src/normadocs/preprocessor.py)) - Extracts metadata from Markdown front matter, builds title pages, joins hard-wrapped lines, converts multiline tables to pipe tables, and inserts page breaks before H1 headings.

2. **Pandoc Conversion** ([pandoc_client.py](src/normadocs/pandoc_client.py)) - Converts processed Markdown to DOCX using Pandoc. Supports bibliography files (.bib) and custom CSL styles.

3. **Formatter** ([formatters/](src/normadocs/formatters/)) - Applies academic formatting to the DOCX using python-docx. Uses a factory pattern:
   - [base.py](src/normadocs/formatters/base.py) - Abstract base class (`DocumentFormatter`)
   - [apa.py](src/normadocs/formatters/apa.py) - APA 7th Edition formatter
   - [icontec.py](src/normadocs/formatters/icontec.py) - ICONTEC formatter
   - [ieee.py](src/normadocs/formatters/ieee.py) - IEEE 8th Edition formatter

### Key Files

| File | Purpose |
|------|---------|
| [cli.py](src/normadocs/cli.py) | Typer-based CLI entry point (`normadocs convert`) |
| [config.py](src/normadocs/config.py) | Constants (margins, fonts, metadata fields) |
| [models.py](src/normadocs/models.py) | `DocumentMetadata` dataclass |
| [pdf_generator.py](src/normadocs/pdf_generator.py) | LibreOffice/WeasyPrint PDF generation |

### CLI Usage

```bash
# Convert Markdown to APA DOCX
normadocs document.md

# Convert with ICONTEC style and generate PDF
normadocs document.md -s icontec -f all

# With bibliography
normadocs document.md -b refs.bib -c apa.csl
```

### Development Notes

- **Python**: 3.10+
- **Type checking**: MyPy is configured with `strict = false`
- **Linting**: Ruff with pycodestyle, pyflakes, isort, and pyupgrade rules
- **Testing**: pytest with pytest-cov (minimum 60% coverage)
- **Security**: Bandit skips B404, B603, B607 (subprocess calls to pandoc/libreoffice are intentional)
