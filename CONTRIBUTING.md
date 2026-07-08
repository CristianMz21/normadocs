# Contributing to NormaDocs

Thanks for your interest in NormaDocs. Contributions from students, researchers,
educators, and developers are welcome. NormaDocs is an early-stage project, so
even small fixes, examples, and docs improvements matter.

## Code of Conduct

By participating, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Local setup

```bash
git clone https://github.com/CristianMz21/normadocs.git
cd normadocs
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -e ".[dev]"
```

### Prerequisites

- **Python 3.10+** — verify with `python --version`.
- **Pandoc on `PATH`** — verify with `pandoc --version`. Install via
  https://pandoc.org/installing.html or your package manager
  (`apt install pandoc`, `brew install pandoc`).
- **PDF support (optional)** — install LibreOffice (`apt install libreoffice`)
  or run `pip install normadocs[pdf]` for the WeasyPrint fallback.

## Quality gates

Run these locally before opening a PR:

```bash
make test       # pytest tests/ -v
make lint       # ruff check + ruff format --check + mypy --strict
make security   # bandit
make check      # lint + test-cov + security
make build      # python3 -m build
```

The CI workflow at `.github/workflows/ci.yml` is the source of truth: it scopes
lint to `src/` and `tests/`, runs mypy with `--strict`, enforces
`--cov-fail-under=78`, and **fails on any inline suppression** (`# noqa`,
`# type: ignore`, `# nosec`, etc.).

## Submitting issues

Use the templates under [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/):

- **Bug Report** — unexpected behavior, crashes, regressions.
- **Feature Request** — new functionality or standard support.
- **Documentation Issue** — gaps, typos, or unclear docs in the README or
  the docs site.

For security vulnerabilities, do **not** open a public issue — see
[SECURITY.md](.github/SECURITY.md).

## Submitting pull requests

1. Fork and create a feature branch (`git checkout -b fix/short-description`).
2. Make focused commits with descriptive messages. Conventional Commits are
   encouraged (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`).
3. Run `make check` locally. CI must pass before a review can start.
4. Open a PR using [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)
   and link any related issue.
5. Keep PRs reviewable — small, single-purpose changes land faster.

## Coding style

- Python 3.10+ syntax (`list[str]`, `str | None`).
- Full type annotations on public APIs; mypy `--strict` must pass.
- `ruff` for lint and formatting (rules `E,F,W,I,UP,B,SIM,RUF`; line length 100).
- **No suppressions.** Do not add `# noqa`, `# type: ignore`, `# nosec`,
  `# pylint:`, or Bandit skips — fix the underlying issue.
- Logging via `logging.getLogger("normadocs")`.
- Subprocess calls go through `src/normadocs/utils/subprocess.py` and must
  check `returncode` and read `stderr` on failure.

See [docs/AGENTS.md](docs/AGENTS.md) for the full code-style guide.

## Documentation contributions

- The user-facing docs source lives at `docs/src/` (MkDocs Material) and is
  deployed to GitHub Pages from there.
- When changing CLI flags, formatter behavior, or the supported standards
  list, update the relevant `docs/src/**/*.md` page as well.
- The agentic dev guide is `AGENTS.md` (root) and `docs/AGENTS.md`. Both are
  reference material for contributors.

## Good first issues

See [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md) for scoped starter
ideas (Markdown examples, Windows docs, error messages, ICONTEC edge cases,
tests).

## Adding a new citation standard

See the dedicated section in [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md#adding-a-new-citation-standard)
— formatter + YAML config + tests + docs checklist.

---

For the full contributor guide, see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).