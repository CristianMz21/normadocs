# AGENTS.md

Compact guide for OpenCode sessions in this repository. For the full code style
guide see [`docs/AGENTS.md`](docs/AGENTS.md). For project narrative and CLI
examples see [`CLAUDE.md`](CLAUDE.md). Don't duplicate those here.

## Project in one paragraph

**NormaDocs** (PyPI package: `normadocs`, repo dir: `APAScript`) converts
Markdown to academically-formatted DOCX/PDF — APA 7th, ICONTEC NTC 1486, IEEE
8th. Pipeline: `MarkdownPreprocessor` → `PandocRunner` (subprocess to
`pandoc`) → `DocumentFormatter` (python-docx) → optional PDF + APA verifier.
CLI entry: `src/normadocs/cli.py` → Typer `normadocs convert`. Python ≥ 3.10.
PEP 561 (`src/normadocs/py.typed`).

## Prerequisites (not in pyproject)

- **`pandoc` on `PATH`** — `apt install pandoc` / `brew install pandoc`. Not a
  pip dep; CI installs via `apt-get`. Missing → every conversion and most
  tests fail.
- **LibreOffice** (`apt install libreoffice-writer`) for `--format pdf|all`,
  or `pip install normadocs[pdf]` for the WeasyPrint fallback.
- **LanguageTool** is opt-in: local server, Docker (`--lt-docker`), or
  download to `/opt/LanguageTool`.

## Commands

```bash
make install      # pip install -e ".[dev]"   (assumes pandoc on PATH)
make test         # pytest tests/ -v          (no coverage gate)
make test-cov     # pytest + coverage; see CI gate table below
make lint         # ruff check . && ruff format --check . && mypy src/normadocs
make format       # ruff format . && ruff check --fix .
make security     # bandit -r src/normadocs -c pyproject.toml
make check        # lint + test-cov + security
make build        # python3 -m build         (note: Makefile uses python3)
```

Single test / focused subset:

```bash
pytest tests/test_cli.py::TestCLI::test_convert_command_success -v
pytest tests/ -k "apa_table" -v
pytest tests/unit/ -q                           # APA unit tests only
pytest tests/test_preprocessor_strict.py -q     # one file
```

## CI / quality gates — read this before submitting

`.github/workflows/ci.yml` is the source of truth, not the Makefile. They
**don't fully agree**:

| Gate      | `make` command            | CI command                                                                                  |
| --------- | ------------------------- | ------------------------------------------------------------------------------------------- |
| Lint      | `ruff check .`            | `ruff check src/ tests/` (no `scripts/`, no `docs/`, no root files)                         |
| Format    | `ruff format --check .`   | `ruff format --check src/ tests/`                                                           |
| MyPy      | `mypy src/normadocs`      | `mypy --strict src/` (`--strict` passed explicitly; `pyproject.toml` already sets it)       |
| Tests     | no coverage gate          | `pytest tests/ -W error --cov-fail-under=78` — warnings become errors                      |
| Python    | local                     | matrix: 3.10, 3.11, 3.12, 3.13                                                             |

`scripts/` is excluded from ruff (`pyproject.toml` → `exclude = ["scripts/"]`).
Put one-off utilities there; they won't be linted.

**Zero-suppression policy.** CI sets `RUFF_NOQA: "1"`, and a final
`annotations-check` job fails the run if GitHub reports **any** annotation
across all jobs. Practical implications:

- **No** `# noqa`, `# type: ignore`, `# nosec`, `# mypy:`, `# RUF###`,
  `# B###` comments anywhere in `src/` or `tests/`. Fix the underlying issue.
- Verify locally with `scripts/find_suppressions.sh [path]`.
- A single Bandit low-severity warning fails CI. Subprocess calls to pandoc /
  libreoffice are intentional (`B404`, `B603`, `B607` are accepted in
  `CLAUDE.md`/CI behaviour but still emit annotations — treat them as fix-or-
  justify).

## Repository layout

```
src/normadocs/
├── cli.py               # Typer `convert` — 9-stage orchestration
├── cli_helpers.py       # Stage implementations (preprocess, pandoc, LT, PDF, verify)
├── preprocessor.py      # Stage 1: metadata, line-joining, cover
├── pandoc_client.py     # Stage 2: subprocess → `pandoc` for MD→DOCX
├── pdf_generator.py     # LibreOffice (preferred) / WeasyPrint fallback
├── languagetool_client.py  # LanguageTool API client (local or Docker)
├── codeimage_processor.py  # {code} blocks
├── config.py            # PAGEBREAK_OPENXML, DEFAULT_OUTPUT_DIR ("ExportDocs"), METADATA_FIELDS
├── models.py            # DocumentMetadata, ProcessOptions dataclasses
├── utils/subprocess.py  # ★ Subprocess wrapper (CommandNotFoundError, returncode check)
├── standards/           # YAML configs: apa7.yaml, icontec.yaml, ieee.yaml + schema.py
├── formatters/
│   ├── apa/             # ★ Real APA 7 implementation (subpackage)
│   ├── apa.py           # Backward-compat shim — DO NOT add code here
│   ├── icontec.py
│   ├── ieee.py
│   └── base.py          # DocumentFormatter ABC + get_config() helper
└── verifier/            # APA 7 post-conversion verification
    ├── apa_verifier.py  # Main orchestrator
    ├── docx_analyzer.py, pdf_analyzer.py
    └── checks/          # margins, fonts, headings, tables, …
```

`formatters/apa.py` re-exports `APADocxFormatter` from `formatters/apa/` on
purpose. New code goes in the subpackage.

Tests:

```
tests/
├── test_*.py            # Top-level integration / CLI / pipeline tests
├── temp_*.docx, temp_*.pdf, temp_debug*/, temp_icontec*/  # gitignored outputs
└── unit/                # Unit tests (apa_*, verifier, docx_analyzer, …)
```

`tests/fixtures/` exists but is empty. `_pandoc_raw.docx` at repo root is an
intermediate artifact (gitignored).

## CLI pipeline (`normadocs convert`)

1. `MarkdownPreprocessor.process()` → `(clean_md, meta)`
2. `_run_codeimage` if `{code}` blocks present
3. Optional LanguageTool **pre-check** (needs `--language-tool`)
4. `_run_pandoc` → `output_dir/{stem}_{STYLE}.docx`
5. Optional LanguageTool **post-check** on the DOCX
6. `_apply_formatting(style, output_docx, meta)` → `get_formatter(style, …)`
7. Optional PDF generation (`--format pdf|all`)
8. Optional APA 7 verification on the PDF (`--verify-apa`, default on)
9. Always: Docker cleanup + optional `--lt-report` write

Defaults: `--style apa`, `--format docx`, `--output-dir ExportDocs/`
(CWD-relative). Output filename: `{stem}_{STYLE_UPPER}.docx` / `.pdf`.
`apa` and `apa7` both resolve to `standards/apa7.yaml` (see `_get_style_key`
in `src/normadocs/standards/__init__.py`).

## Conventions that differ from defaults

- **MyPy** `strict = true` + `ignore_missing_imports = true`. All public
  functions typed. Use `str | None`, not `Optional[str]`.
- **Ruff** line length 100; rules: E, F, W, I, UP, B, SIM, RUF.
- **Typer**: use `Annotated[Param, typer.Argument(...)]` / `typer.Option(...)`,
  not the old `=typer.Option(...)` default syntax.
- **Subprocess**: prefer `src/normadocs/utils/subprocess.py` wrapper; always
  check `returncode` and read `result.stderr` on failure. `FileNotFoundError`
  means pandoc/libreoffice is missing.
- **YAML config access** in formatters: use the `get_config(*keys, default=…)`
  helper (dot-notation traversal), not chained `.get()`.
- **CLI errors**: `typer.echo(..., err=True)` + `raise typer.Exit(code=1)`.
  Chain with `raise … from None` for expected/user-facing errors.
- **Logger**: module-level `logger = logging.getLogger("normadocs")`.
- **Version source of truth**: `pyproject.toml` (`0.2.1`).
  `src/normadocs/__init__.py` says `0.2.0` and is **stale** — don't read it.

## Things easy to miss

- **OpenCode config** lives at `.opencode/opencode.json` (not the user-level
  one) and pulls three instruction files into every session: `AGENTS.md` (this
  file), `.specify/memory/constitution.md`, and `.opencode/MANDATORY_SKILLS.md`.
  Project-local mandatory skills are listed in the latter — load them via
  the `skill` tool when their trigger matches.
- **`.specify/memory/constitution.md` is currently an unfilled template**
  (placeholder text like `[PRINCIPLE_1_NAME]`). Don't infer governance from
  it — it's a stub. The real workflow contract is this file and the CI rules.
- **`CLAUDE.md` ≠ `AGENTS.md`.** `CLAUDE.md` is the project brief (overview,
  architecture, CLI examples, code standards). This file is the agent
  workflow guide (CI gates, gotchas, conventions that bite). They're
  complementary, not duplicates.
- **MkDocs source is `docs/src/`**, not `docs/` root. `docs/mkdocs.yml`
  → `docs_dir: src`. Edit markdown there for published docs.
- **`IDocs/`, `ExportDocs/`** referenced in `.claude/settings.local.json` are
  the user's local working directories, not part of this repo. Don't try to
  read them — they won't exist in a fresh checkout.
- **Adding a new citation standard**: create `formatters/<name>.py` (or
  subpackage), register in `formatters/__init__.py::get_formatter`, add
  `standards/<name>.yaml`, add tests under `tests/` and `tests/unit/`.
  See `docs/CONTRIBUTING.md` for the full checklist.
- **PR template** (`.github/PULL_REQUEST_TEMPLATE.md`) requires linking
  related issues and the full `make check` to pass.

## Don't

- Don't add `# noqa`, `# type: ignore`, `# nosec`, `# mypy:`, or any
  Bandit/Ruff inline suppression — CI will fail.
- Don't edit `formatters/apa.py`; it's a backward-compat shim.
- Don't trust the version in `src/normadocs/__init__.py`.
- Don't run `make lint` and assume CI will agree — CI scopes lint to
  `src/ tests/`.
- Don't commit `tests/temp_*`, `examples/ExportDocs/*.docx|pdf`,
  `coverage.xml`, `.coverage`, or `_pandoc_raw.docx` — all gitignored.
- Don't run `make publish` (twine upload) without explicit user approval.
- Don't treat `.specify/memory/constitution.md` as authoritative — it's a
  template, not a live contract.
