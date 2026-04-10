# CLI Reference

Complete reference for the `normadocs` command-line interface.

## Commands

### normadocs convert

Converts a Markdown file to a formatted DOCX/PDF.

```bash
normadocs convert INPUT_FILE [OPTIONS]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `INPUT_FILE` | Path to input Markdown file (required) |

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output-dir` | `-o` | Output directory | `./output` |
| `--format` | `-f` | Output format: `docx`, `pdf`, or `all` | `docx` |
| `--style` | `-s` | Citation style: `apa`, `icontec`, `ieee` | `apa` |
| `--bibliography` | `-b` | BibTeX file for citations | - |
| `--csl` | `-c` | CSL style file | - |
| `--language-tool` | - | Enable LanguageTool checking | `false` |
| `--lt-strict` | - | Strict LanguageTool mode | `false` |

**Examples:**
```bash
# Basic conversion (APA style)
normadocs document.md

# ICONTEC style with PDF
normadocs document.md -s icontec -f all

# With bibliography
normadocs document.md -b refs.bib -c apa.csl

# With LanguageTool
normadocs document.md --language-tool
```

### normadocs --version

Shows the installed version.

```bash
normadocs --version
```

### normadocs --help

Shows help information.

```bash
normadocs --help
```