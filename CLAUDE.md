# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NormaDocs converts Markdown documents to academically-formatted DOCX/PDF files (APA 7th Edition, ICONTEC NTC 1486, IEEE 8th Edition). It provides automatic title pages, bibliography support (BibTeX/CSL), and applies formatting rules using python-docx.

## Common Commands

```bash
make install      # Install with dev dependencies (requires Pandoc installed)
make test         # Run pytest
make test-cov     # Run tests with coverage (minimum 78%)
make lint         # ruff check + format check + mypy
make format       # Auto-format code
make security     # Bandit security scan
make check        # Full quality gate (lint + test-cov + security)
make build        # Build wheel + sdist
```

**Prerequisite**: Pandoc must be installed (`pandoc --version`). Install via your system package manager or from https://pandoc.org/installing.html.

## Architecture

Three-stage pipeline:

1. **Preprocessor** (`src/normadocs/preprocessor.py`) — Extracts metadata (title, author, keywords), builds cover pages, joins hard-wrapped lines, converts multiline tables to pipe tables
2. **PandocRunner** (`src/normadocs/pandoc_client.py`) — Converts Markdown to DOCX, handles BibTeX bibliography and CSL styles
3. **DocumentFormatter** (`src/normadocs/formatters/`) — Applies academic formatting (fonts, margins, spacing, tables). Factory pattern:
   - `formatters/apa.py` — APA 7th Edition
   - `formatters/icontec.py` — ICONTEC NTC 1486
   - `formatters/ieee.py` — IEEE 8th Edition

## Key Files

| File | Purpose |
|------|---------|
| `src/normadocs/cli.py` | Typer CLI entry point (`normadocs convert`) |
| `src/normadocs/config.py` | Constants (margins, fonts, metadata field names) |
| `src/normadocs/models.py` | `DocumentMetadata` dataclass, `ProcessOptions` |
| `src/normadocs/pdf_generator.py` | PDF via LibreOffice or WeasyPrint |
| `src/normadocs/languagetool_client.py` | LanguageTool grammar checking |
| `src/normadocs/standards/*.yaml` | YAML configs for each citation standard |

## CLI Examples

```bash
normadocs document.md                          # APA by default
normadocs document.md -s icontec -f all        # ICONTEC + PDF
normadocs document.md -b refs.bib -c apa.csl    # With bibliography
```

## Code Standards

- **Type checking**: MyPy `strict = true` (configured in pyproject.toml)
- **Linting**: Ruff (pycodestyle, pyflakes, isort, pyupgrade, bugbear)
- **Testing**: pytest with pytest-cov, minimum 78% coverage
- **Security**: Bandit (excludes B404, B603, B607 — subprocess calls to pandoc/libreoffice are intentional)

## Version

Current version is defined in `pyproject.toml` (`version = "0.2.1"`). The `__version__` in `src/normadocs/__init__.py` may be stale and should not be relied upon.
