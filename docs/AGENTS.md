# AGENTS.md

Agentic coding guidelines for NormaDocs — Markdown to academic DOCX/PDF converter.

## Project Overview

NormaDocs converts Markdown documents to academic-standard DOCX/PDF formats (APA 7th, ICONTEC, IEEE). The pipeline has three stages: **Preprocessor** → **Pandoc** → **Formatter**.

**Requirement**: Pandoc must be installed for conversion to work.

---

## Build / Lint / Test Commands

### Installation
```bash
make install          # Install dev dependencies: pip install -e ".[dev]"
```

### Testing
```bash
make test            # Run all tests with verbose output
make test-cov        # Run tests with coverage (minimum 78%)

# Single test file
pytest tests/test_cli.py -v

# Single test function
pytest tests/test_cli.py::TestCLI::test_convert_command_success -v

# Single test using -k pattern
pytest tests/ -k "test_convert" -v
```

### Linting
```bash
make lint            # ruff check + ruff format check + mypy
make format          # Auto-fix linting issues: ruff format . && ruff check --fix .
```

### Security
```bash
make security        # Bandit scan (skips B404, B603, B607 for intentional subprocess calls)
```

### Quality Gates
```bash
make check           # lint + test-cov + security (all quality gates)
```

### Build
```bash
make build           # Build wheel + sdist
make clean           # Remove build artifacts and caches
```

---

## Code Style

### General
- **Language**: Python 3.10+
- **Line length**: 100 characters (configured in ruff)
- **Type checking**: MyPy with `strict = true`
- **Docstrings**: Use triple quotes for modules and public APIs

### Formatting
- Use **ruff format** for all formatting (4-space indent, etc.)
- Use `python -m ruff format .` or `make format` to auto-format

### Imports
- **Order**: Standard library → Third-party → Local (following isort rules)
- **Explicit relative imports** for intra-package imports: `from .module import ...` or `from ..module import ...`
- **Known first-party**: `normadocs` (configured in ruff)

```python
# Correct
from pathlib import Path
from typing import Annotated

import typer
from docx import Document

from .config import DEFAULT_OUTPUT_DIR
from .formatters import get_formatter
from .models import DocumentMetadata
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Modules | lowercase, snake_case | `preprocessor.py`, `languagetool_client.py` |
| Classes | PascalCase | `DocumentMetadata`, `MarkdownPreprocessor`, `PandocRunner` |
| Functions/methods | snake_case | `extract_metadata()`, `process()` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_OUTPUT_DIR`, `PAGEBREAK_OPENXML` |
| Type variables | PascalCase or snake_case | `list[str]`, `dict[str, str]` |
| Private members | _leading_underscore | `_is_special_line()`, `_join_wrapped_lines()` |

### Types
- Use **type hints** for all function signatures
- Use `| None` syntax (Python 3.10+ union syntax, not `Optional[]`)
- Use `from typing import Annotated` for CLI argument annotations with Typer
- Annotate return types explicitly; don't use `-> None` for void returns in abstract methods

```python
# Good
def extract_metadata(lines: list[str]) -> DocumentMetadata:
    ...

def process(self, text: str) -> tuple[str, DocumentMetadata]:
    ...

# Good - using | None syntax
author: str | None = None

# For Typer CLI arguments
input_file: Annotated[Path, typer.Argument(help="Input Markdown file", exists=True, readable=True)]
```

### Data Classes
Use `@dataclass` for simple data models:

```python
from dataclasses import dataclass, field

@dataclass
class DocumentMetadata:
    title: str = "Untitled"
    author: str | None = None
    extra: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "DocumentMetadata":
        ...
```

### Error Handling
- **CLI errors**: Use `typer.echo(..., err=True)` and `raise typer.Exit(code=1)`
- **Graceful degradation**: Return `False` or `None` on failure; let caller decide
- **Subprocess errors**: Check `returncode != 0`, handle `FileNotFoundError`
- **Chaining exceptions**: Use `raise ... from None` to suppress traceback for expected errors

```python
# CLI error handling pattern
try:
    content = input_path.read_text(encoding="utf-8")
    clean_md, meta = preprocessor.process(content)
except Exception as e:
    typer.echo(f"Error processing Markdown: {e}", err=True)
    raise typer.Exit(code=1) from None

# Subprocess error handling pattern
try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ Pandoc error:\n{result.stderr}", file=sys.stderr)
        return False
except FileNotFoundError:
    print("  ✗ Error: Pandoc not found on the system.", file=sys.stderr)
    return False
```

### Logging
- Use `logging.getLogger("normadocs")` for module-level loggers
- Configure with `logging.basicConfig(level=logging.INFO, format="%(message)s")`
- Use `logger.info()` / `logger.error()` instead of print for significant events

```python
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("normadocs")
```

### Testing
- Use **pytest** with **unittest** patterns
- Use `unittest.mock.MagicMock` and `@patch` for mocking
- Use `Typer.CliRunner` for CLI testing
- Place tests in `tests/` directory with `test_*.py` naming

```python
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

from normadocs.cli import app

runner = CliRunner()

class TestCLI(unittest.TestCase):
    @patch("normadocs.cli.PandocRunner")
    @patch("normadocs.cli.get_formatter")
    def test_convert_command_success(self, mock_get_fmt, mock_pandoc):
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent")
            result = runner.invoke(app, ["test.md"])
            self.assertEqual(result.exit_code, 0)
```

### Architecture Patterns

**Pipeline Pattern** (Preprocessor → Pandoc → Formatter):
```
MarkdownPreprocessor.process(content) → (clean_md, DocumentMetadata)
       ↓
PandocRunner.run(clean_md, output_path, bibliography, csl) → bool
       ↓
DocumentFormatter.process(meta) + .save(output_path)
```

**Factory Pattern** for Formatters with YAML Config:
```python
from .formatters import get_formatter

# Factory loads YAML config automatically
formatter = get_formatter(style, docx_path)
formatter.process(metadata)
formatter.save(output_path)

# Or pass custom config to override YAML defaults
custom_config = {"fonts": {"body": {"name": "Arial", "size": 12}}}
formatter = get_formatter("apa", docx_path, config=custom_config)
```

**Abstract Base Class** for Formatters:
```python
from abc import ABC, abstractmethod

class DocumentFormatter(ABC):
    def __init__(self, doc_path: str, config: dict[str, Any] | None = None):
        self.doc_path = doc_path
        self.doc = Document(doc_path)
        self.config = config if config is not None else {}

    def get_config(self, *keys: str, default: Any = None) -> Any:
        """Get nested config value using dot notation keys."""
        ...

    @abstractmethod
    def process(self, meta: DocumentMetadata) -> None:
        pass

    @abstractmethod
    def save(self, output_path: str) -> None:
        pass
```

### YAML Configuration System

Standards are defined in `src/normadocs/standards/` as YAML files:

```
src/normadocs/standards/
├── __init__.py      # StandardLoader + preloaded configs
├── loader.py        # StandardLoader class
├── schema.py        # Default configs for each standard
├── apa7.yaml        # APA 7th Edition configuration
├── icontec.yaml     # ICONTEC (NTC 1486) configuration
└── ieee.yaml        # IEEE 8th Edition configuration
```

**Config Structure** (apa7.yaml example):
```yaml
fonts:
  body: {name: "Times New Roman", size: 12}
  headings:
    name: "Times New Roman"
    level1: {alignment: "center", bold: true}
margins:
  unit: inches
  top: 1.0
  bottom: 1.0
  left: 1.0
  right: 1.0
spacing:
  line: double  # or 1.5, single
tables:
  caption_prefix: "Table"
  caption_above: true
  note_suffix: "Author's elaboration."
figures:
  caption_prefix: "Figure"
```

**Loading Config:**
```python
from .standards import StandardLoader, get_default_config, merge_with_defaults

# Load from YAML (merged with defaults)
loader = StandardLoader()
config = loader.load("apa7")

# Get defaults
defaults = get_default_config("apa")

# Merge custom config with defaults
final = merge_with_defaults(custom_config, "apa")
```

**Config Access in Formatters:**
```python
# Via get_config helper (dot notation)
body_font = self.get_config("fonts", "body", "name", default="Times New Roman")

# Or directly from config dict
body_font = self.config.get("fonts", {}).get("body", {}).get("name", "Times New Roman")
```

### File Structure
```
src/normadocs/
├── __init__.py              # Package init (version, exports)
├── cli.py                   # Typer CLI entry point
├── cli_helpers.py           # CLI helper functions (orchestration)
├── config.py                # Constants (PAGEBREAK_OPENXML, OUTPUT_DIR)
├── models.py                # Dataclasses (DocumentMetadata, ProcessOptions)
├── preprocessor.py          # MarkdownPreprocessor (Stage 1)
├── pandoc_client.py         # PandocRunner (Stage 2)
├── pdf_generator.py         # PDFGenerator (LibreOffice/WeasyPrint fallback)
├── languagetool_client.py   # LanguageTool API client
├── standards/               # YAML configuration files
│   ├── __init__.py          # StandardLoader + preloaded configs
│   ├── loader.py            # StandardLoader class
│   ├── schema.py            # Default configs + merge utilities
│   ├── apa7.yaml            # APA 7th Edition configuration
│   ├── icontec.yaml         # ICONTEC (NTC 1486) configuration
│   └── ieee.yaml            # IEEE 8th Edition configuration
└── formatters/
    ├── __init__.py          # get_formatter() factory + load_standard_config()
    ├── base.py              # Abstract DocumentFormatter (ABC)
    ├── apa/
    │   ├── __init__.py
    │   ├── apa_formatter.py # Main APA formatter orchestrator
    │   ├── apa_styles.py    # Styles + fonts (reads config)
    │   ├── apa_page.py      # Margins + page numbers (reads config)
    │   ├── apa_cover.py     # Cover page (reads config)
    │   ├── apa_paragraphs.py # Paragraph formatting (reads config)
    │   ├── apa_tables.py    # Tables + captions (reads config)
    │   ├── apa_figures.py   # Figures + captions (reads config)
    │   └── apa_keywords.py  # Keywords + foreign words
    ├── icontec.py           # ICONTEC formatter
    └── ieee.py              # IEEE 8th Edition formatter
```

---

## Lint Configuration

Ruff configuration (from `pyproject.toml`):
- **Line length**: 100
- **Target Python**: 3.10
- **Rules enabled**: E, F, W, I, UP, B, SIM, RUF
- **Ignored**: E501 (line too long), B008 (function calls in argument defaults for Typer)

Bandit skips: B404, B603, B607 (subprocess calls to pandoc/libreoffice are intentional).

---

## Common Issues / Gotchas

1. **Pandoc dependency**: If Pandoc is not installed, conversion will fail. Ensure it's available in PATH.

2. **Subprocess stderr**: Always check `result.stderr` when pandoc/subprocess calls fail.

3. **File encoding**: Use `encoding="utf-8"` explicitly when reading/writing files.

4. **Path handling**: Use `pathlib.Path` for path operations; avoid string concatenation.

5. **Typer argument order**: Required arguments come before options; use `Annotated` for all CLI args with metadata.

6. **DOCX manipulation**: Use `python-docx` for DOCX operations; `Document(doc_path)` to load existing files.

7. **Markdown preprocessing**: The preprocessor joins hard-wrapped lines, converts multiline tables to pipe tables, and inserts page breaks before H1 headings.

8. **Coverage minimum**: 78% — new code should maintain or exceed this threshold.