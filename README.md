# NormaDocs

[![PyPI Version](https://img.shields.io/pypi/v/normadocs.svg)](https://pypi.org/project/normadocs/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![CI](https://github.com/CristianMz21/normadocs/actions/workflows/ci.yml/badge.svg)](https://github.com/CristianMz21/normadocs/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Checked](https://img.shields.io/badge/typed-PEP%20561-brightgreen)](https://peps.python.org/pep-0561/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**NormaDocs** is a professional open-source tool that converts Markdown documents to academically-formatted DOCX and PDF files, with full support for major citation standards.

## Features

- **Multiple Citation Standards**: APA 7th Edition, ICONTEC (NTC 1486), IEEE 8th Edition
- **Automatic Cover Pages**: Title, author, institution, program, date extraction
- **Complete Formatting**: Margins, typography, and spacing per selected standard
- **Table of Contents**: Automatic detection and formatting of `# Heading` sections
- **APA Tables**: Horizontal borders, no vertical lines, captions with _Table X_ format
- **Bibliography Support**: BibTeX (`.bib`) files and CSL styles via Pandoc
- **Dual Output**: DOCX always, PDF optionally (LibreOffice or WeasyPrint)
- **Two Interfaces**: CLI (`normadocs`) or Python library import
- **PEP 561 Typed**: Package includes `py.typed` marker for static type checkers
- **Quality Gates**: CI blocks publication if linting, tests, or security scans fail

## Supported Standards

| Standard | Status | Font | Spacing | Typical Use |
|----------|--------|------|---------|-------------|
| **APA 7th Edition** | ✅ Complete | Times New Roman 12pt | Double | Social Sciences |
| **ICONTEC (NTC 1486)** | ✅ Complete | Arial 12pt | 1.5 lines | Colombian Academic |
| **IEEE 8th Edition** | ✅ Complete | Times New Roman 10pt | Single | Engineering/Technical |

## Installation

### Prerequisites

- **Python** 3.10 or higher
- **[Pandoc](https://pandoc.org/installing.html)** — required for Markdown to DOCX conversion

### From PyPI

```bash
pip install normadocs
```

#### Optional Extras

```bash
# PDF generation with WeasyPrint
pip install normadocs[pdf]

# Development dependencies (linting, testing, security)
pip install normadocs[dev]
```

### From Source

```bash
git clone https://github.com/CristianMz21/normadocs.git
cd normadocs
pip install -e ".[dev]"
```

### PDF Dependencies

For PDF output, install **one** of the following:

- **LibreOffice** (recommended): `sudo apt install libreoffice`
- **WeasyPrint**: `pip install normadocs[pdf]`

## Quick Start

### CLI

```bash
# Full help
normadocs --help

# Basic conversion (APA by default)
normadocs my_document.md

# Specify ICONTEC standard
normadocs my_document.md --style icontec

# With BibTeX bibliography + custom CSL style
normadocs my_document.md --bibliography refs.bib --csl apa.csl

# Generate PDF in addition to DOCX
normadocs my_document.md --format pdf

# Custom output directory
normadocs my_document.md -o ./Submissions -s apa -f all
```

### Python Library

```python
from pathlib import Path
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.pandoc_client import PandocRunner
from normadocs.formatters import get_formatter

# 1. Pre-process Markdown
input_md = Path("paper.md").read_text(encoding="utf-8")
processor = MarkdownPreprocessor()
clean_md, metadata = processor.process(input_md)

# 2. Convert to DOCX via Pandoc
PandocRunner().run(clean_md, "output.docx")

# 3. Apply academic formatting
formatter = get_formatter("apa", "output.docx")
formatter.process(metadata)
formatter.save("output_final.docx")
```

## Input Markdown Format

NormaDocs extracts metadata from the first lines of your Markdown file:

```markdown
**Document Title**

Author Name
Program Name
Course Number
Institution Name
Faculty
2026-04-10

# Abstract

This is the abstract text...

**Keywords:** keyword1, keyword2, keyword3

# Introduction

Document content goes here...

# References

Author, A. A. (2024). Title. _Journal_, 1(2), 3-4.
```

> **Note**: The first 2 lines form the title. Lines 3–13 map to: `author`, `program`, `course`, `institution`, `faculty`, `date`.

## Development

```bash
make install      # Install in editable mode with dev dependencies
make lint         # Ruff check + format check + MyPy type check
make test         # Run all tests with pytest
make test-cov     # Run tests with coverage report (minimum 78%)
make security     # Security scan with Bandit
make check        # Full quality gate: lint + test-cov + security
make build        # Build wheel + sdist packages
make clean        # Remove build artifacts and caches
```

## Project Structure

```
normadocs/
├── src/normadocs/              # Main package
│   ├── __init__.py              # Version and exports
│   ├── cli.py                   # Typer CLI entry point
│   ├── cli_helpers.py           # CLI orchestration helpers
│   ├── config.py                # Constants and defaults
│   ├── models.py                # DocumentMetadata, ProcessOptions
│   ├── preprocessor.py          # Stage 1: Markdown preprocessing
│   ├── pandoc_client.py         # Stage 2: Pandoc conversion
│   ├── pdf_generator.py         # PDF generation (LibreOffice/WeasyPrint)
│   ├── languagetool_client.py   # LanguageTool grammar checking
│   ├── py.typed                 # PEP 561 type marker
│   ├── standards/               # YAML configuration files
│   │   ├── apa7.yaml            # APA 7th Edition config
│   │   ├── icontec.yaml         # ICONTEC NTC 1486 config
│   │   └── ieee.yaml            # IEEE 8th Edition config
│   └── formatters/              # Stage 3: Document formatting
│       ├── base.py              # Abstract base formatter
│       ├── apa/                 # APA 7th Edition formatter
│       ├── icontec.py           # ICONTEC formatter
│       └── ieee.py              # IEEE formatter
├── tests/                       # Test suite (pytest + unittest)
├── docs/                        # Documentation site (MkDocs)
├── examples/                    # Example documents
├── scripts/                     # Utility scripts
├── .github/
│   └── workflows/               # CI/CD pipelines
│       ├── ci.yml               # Lint, type check, security, tests
│       ├── release.yml          # PyPI publication
│       ├── docker-publish.yml   # Docker image publication
│       └── docs.yml             # Documentation deployment
├── pyproject.toml               # Project configuration
├── Makefile                     # Development commands
├── Dockerfile                   # Docker image definition
└── README.md                    # This file
```

## CI/CD Pipeline

Publication to **PyPI** and **Docker Hub** is blocked if any quality gate fails:

```
Ruff Lint → MyPy → Bandit → Tests (Python 3.10/3.11/3.12) → Build Check → Annotations Check
```

| Workflow | Trigger | Action |
|----------|---------|--------|
| `ci.yml` | Push to `main`, PR | Lint, type check, security scan, tests, build validation |
| `release.yml` | Tag `v*.*.*` | Publish to PyPI (only if CI passes) |
| `docker-publish.yml` | Push to `main`, tag | Build and publish Docker image to GHCR |
| `docs.yml` | Push to `main` | Deploy MkDocs documentation to GitHub Pages |

## Architecture

NormaDocs uses a three-stage pipeline:

```
Markdown Input
     │
     ▼
┌─────────────────────┐
│  Stage 1: Preprocess │  MarkdownPreprocessor
│  - Extract metadata  │  - Title, author, keywords
│  - Generate cover    │  - Cover page assembly
│  - Join lines        │  - Hard-wrap removal
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  Stage 2: Convert    │  PandocRunner
│  - Markdown → DOCX   │  - BibTeX processing
│  - Bibliography     │  - CSL style application
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  Stage 3: Format     │  DocumentFormatter (ABC)
│  - Apply styles      │  - Fonts, margins, spacing
│  - Format tables     │  - APA/IEEE/ICONTEC rules
│  - Add page numbers  │  - Table of contents
└─────────────────────┘
     │
     ▼
DOCX/PDF Output
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/src/contributing.md) for guidelines.

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## Links

- [Documentation](https://cristianmz21.github.io/normadocs/)
- [PyPI Package](https://pypi.org/project/normadocs/)
- [Issue Tracker](https://github.com/CristianMz21/normadocs/issues)
- [Source Code](https://github.com/CristianMz21/normadocs)
