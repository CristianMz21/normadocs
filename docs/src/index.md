# NormaDocs

[![PyPI Version](https://img.shields.io/pypi/v/normadocs.svg)](https://pypi.org/project/normadocs/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![CI](https://github.com/CristianMz21/normadocs/actions/workflows/ci.yml/badge.svg)](https://github.com/CristianMz21/normadocs/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**NormaDocs** is a professional open-source tool that converts Markdown documents to academically-formatted DOCX and PDF files, with full support for major citation standards.

## Features

- **Multiple Citation Standards**: APA 7th Edition, ICONTEC (NTC 1486), IEEE 8th Edition
- **Automatic Cover Pages**: Title, author, institution, program, date extraction
- **Complete Formatting**: Margins, typography, and spacing per selected standard
- **Bibliography Support**: BibTeX (`.bib`) files and CSL styles via Pandoc
- **PDF Generation**: LibreOffice or WeasyPrint
- **LanguageTool Integration**: Grammar and spell checking

## Quick Start

```bash
pip install normadocs

# Convert to APA (default)
normadocs document.md

# Convert to ICONTEC with PDF output
normadocs document.md --style icontec --format pdf

# Custom output directory
normadocs document.md -o ./Submissions -s apa -f all
```

## Supported Standards

| Standard | Status | Font | Spacing | Typical Use |
|----------|--------|------|---------|-------------|
| **APA 7th Edition** | ✅ Complete | Times New Roman 12pt | Double | Social Sciences |
| **ICONTEC (NTC 1486)** | ✅ Complete | Arial 12pt | 1.5 lines | Colombian Academic |
| **IEEE 8th Edition** | ✅ Complete | Times New Roman 10pt | Single | Engineering/Technical |

## Documentation

- [Installation](installation.md) — Detailed installation instructions
- [CLI Usage](usage/cli.md) — Command-line interface reference
- [Library Usage](usage/library.md) — Using NormaDocs as a Python library
- [Supported Standards](standards/index.md) — APA 7th, ICONTEC, IEEE formatting details
- [Troubleshooting](troubleshooting.md) — Common issues and solutions
- [Contributing](contributing.md) — Development guidelines

## Links

- [Source Code](https://github.com/CristianMz21/normadocs)
- [Issue Tracker](https://github.com/CristianMz21/normadocs/issues)
- [PyPI Package](https://pypi.org/project/normadocs/)
