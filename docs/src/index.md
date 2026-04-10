# NormaDocs

**NormaDocs** is a professional open-source tool that converts Markdown documents to academic-standard DOCX/PDF formats (APA 7th, ICONTEC, IEEE).

## Features

- **Multiple Standards**: APA 7th, ICONTEC NTC 1486, IEEE 8th
- **Automatic Formatting**: Cover pages, margins, fonts, spacing
- **Bibliography Support**: BibTeX and CSL styles
- **PDF Generation**: LibreOffice or WeasyPrint
- **LanguageTool Integration**: Grammar and spell checking

## Quick Start

```bash
pip install normadocs

# Convert to APA (default)
normadocs document.md

# Convert to ICONTEC with PDF
normadocs document.md -s icontec -f all
```

## Supported Standards

| Standard | Field | Font | Spacing |
|----------|-------|------|---------|
| APA 7th | Social Sciences | Times New Roman 12pt | Double |
| ICONTEC | Colombian Academic | Arial 12pt | 1.5 |
| IEEE | Engineering/Technical | Times New Roman 10pt | Single |

## Links

- [Installation](installation.md)
- [CLI Usage](usage/cli.md)
- [Library Usage](usage/library.md)
- [Supported Standards](standards/index.md)
- [Troubleshooting](troubleshooting.md)
- [Contributing](contributing.md)
