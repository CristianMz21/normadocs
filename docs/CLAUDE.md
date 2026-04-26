# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NormaDocs** is a professional open-source tool that converts Markdown documents to academic-standard DOCX/PDF formats (APA 7th Edition, ICONTEC NTC 1486, IEEE 8th Edition). It provides automatic title pages, bibliography support (BibTeX/CSL), and applies formatting rules programmatically using python-docx.

## Common Commands

```bash
# Install development dependencies
make install

# Run tests
make test

# Run tests with coverage (minimum 78%)
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

**Prerequisite**: Pandoc must be installed on the system for conversion to work. Install via your system package manager or from https://pandoc.org/installing.html.

## Architecture

The project follows a **pipeline architecture** with three main stages:

1. **Preprocessor** (`src/normadocs/preprocessor.py`) - Extracts metadata from YAML frontmatter, builds title pages, joins hard-wrapped lines, converts multiline tables to pipe tables, and inserts page breaks before H1 headings.

2. **Pandoc Conversion** (`src/normadocs/pandoc_client.py`) - Converts processed Markdown to DOCX using Pandoc. Supports bibliography files (.bib) and custom CSL styles.

3. **Formatter** (`src/normadocs/formatters/`) - Applies academic formatting to the DOCX using python-docx. Uses a factory pattern:
   - `formatters/base.py` - Abstract base class (`DocumentFormatter`)
   - `formatters/apa/` - APA 7th Edition formatter subpackage
   - `formatters/icontec.py` - ICONTEC formatter
   - `formatters/ieee.py` - IEEE 8th Edition formatter

### Key Files

| File | Purpose |
|------|---------|
| `src/normadocs/cli.py` | Typer-based CLI entry point (`normadocs convert`) |
| `src/normadocs/config.py` | Constants (margins, fonts, metadata fields) |
| `src/normadocs/models.py` | `DocumentMetadata` dataclass |
| `src/normadocs/pdf_generator.py` | LibreOffice/WeasyPrint PDF generation |

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
- **Type checking**: MyPy with `strict = true`
- **Linting**: Ruff with pycodestyle, pyflakes, isort, pyupgrade, and bugbear rules
- **Testing**: pytest with pytest-cov (minimum 78% coverage)
- **Security**: Bandit skips B404, B603, B607 (subprocess calls to pandoc/libreoffice are intentional)