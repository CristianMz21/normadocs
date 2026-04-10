# Contributing to NormaDocs

Thank you for your interest in contributing to **NormaDocs**! We welcome contributions from students, researchers, and developers.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/CristianMz21/normadocs.git
   cd normadocs
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or .venv\Scripts\activate  # Windows
   ```
4. **Install in development mode**:

   ```bash
   pip install -e ".[dev]"
   ```

   This installs the package with linting, testing, and security tools.

5. **Verify Pandoc is installed** (required for integration and E2E tests):
   ```bash
   pandoc --version
   ```

## Development Workflow

1. **Create a branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. **Make your changes** following our code style guidelines.
3. **Run the full quality check**:

   ```bash
   make check   # Runs: lint + test-cov + security
   ```

   Or run individually:

   ```bash
   make lint       # Ruff check + Ruff format + MyPy
   make test       # pytest
   make test-cov   # pytest + coverage (min 60%)
   make security   # Bandit security scan
   ```

4. **Commit** with descriptive messages.
5. **Push** and submit a **Pull Request**.

## Code Style

| Tool          | Purpose                               | Config           |
| ------------- | ------------------------------------- | ---------------- |
| `ruff check`  | Linting (E, F, W, I, UP, B, SIM, RUF) | `pyproject.toml` |
| `ruff format` | Code formatting                       | `pyproject.toml` |
| `mypy`        | Static type checking                  | `pyproject.toml` |
| `bandit`      | Security scanning                     | `pyproject.toml` |

- **Python**: 3.10+
- **Types**: Use modern syntax (`list[str]` not `List[str]`, `str | None` not `Optional[str]`)
- **Imports**: Sorted by `ruff` (isort-compatible)
- **Exceptions**: Always use `raise ... from err` or `raise ... from None`

## Adding a New Citation Standard

To implement support for a new standard (e.g., IEEE, Vancouver):

1. **Create the formatter** in `src/normadocs/formatters/` (e.g., `ieee.py`):

   ```python
   from .base import DocumentFormatter
   from ..models import DocumentMetadata

   class IEEEFormatter(DocumentFormatter):
       def process(self, meta: DocumentMetadata) -> None:
           self._setup_page_layout()
           self._create_styles()
           self._add_cover_page(meta)
           self._process_paragraphs()

       def save(self, output_path: str) -> None:
           self.doc.save(str(output_path))
   ```

2. **Register it** in `src/normadocs/formatters/__init__.py`:

   ```python
   from .ieee import IEEEFormatter

   def get_formatter(style: str = "apa", doc_path: str = "") -> DocumentFormatter:
       # ... existing code ...
       elif style == "ieee":
           return IEEEFormatter(doc_path)
   ```

3. **Add tests**:
   - Unit test in `tests/test_formatters.py`
   - E2E test in `tests/test_e2e.py` (follow the `TestEndToEndICONTEC` pattern)

4. **Update documentation**:
   - Add the standard to the table in `README.md`
   - Update `CLI --help` if needed

## Pull Request Guidelines

- Provide a clear title and description of your changes.
- Link to any relevant issues.
- Ensure **all CI checks pass** (`make check` must be green).
- Add tests for new features or bug fixes.
- Update documentation if behavior changes.

> ⚠️ **Important**: CI must pass before any PR can be merged. The pipeline runs
> lint, type checking, security scan, and tests with coverage.

## Reporting Issues

When reporting a bug, please include:

- Python version (`python --version`)
- Pandoc version (`pandoc --version`)
- OS and version
- The Markdown file content (or a minimal reproducer)
- Full error output

Thank you for contributing! 🎉
