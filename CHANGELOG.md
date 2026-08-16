# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **SonarCloud findings resolved without suppressions** (security D →
  target A, reliability C → target A, ~90 code smells):
  - All GitHub Actions third-party actions pinned to full commit SHAs;
    workflow-level permissions moved to job level (least privilege);
    every CI install switched to locked resolution (`uv sync --frozen`
    from `uv.lock`, new `docs/requirements.lock` with
    `--only-binary :all:`).
  - Dockerfile: explicit `COPY` instead of `COPY . .`, non-root `appuser`,
    locked `uv sync --frozen --no-dev` install, sorted apt packages.
  - `languagetool_client`: remote LanguageTool servers now default to
    HTTPS; plain HTTP is kept only for loopback hosts (checked via
    `ipaddress`, fixing Sonar S5332 and a Bandit B104 false positive in
    one move).
  - `icontec`: float equality on the configured 1.5 line spacing replaced
    with `math.isclose` (S1244).
  - `verify_pdf`/`verify_calculations` scripts: regex fixes (explicit
    precedence groups, negated character classes instead of reluctant
    quantifiers, simplified citation pattern), unused parameters removed.
  - `verify_all_calculations`: fixed a duplicated `for row in table.rows`
    clause in the row-protection check (real bug found by the cleanup).
  - Naming: 141 camelCase XML-helper locals renamed to snake_case
    (S117); duplicated literals extracted to constants (`DEFAULT_BODY_FONT`
    in `config.py`, per-file OOXML qname constants, reference-heading
    consolidation via `REFERENCE_HEADINGS`, `Nota.`/`et al.` prefixes).
  - Tests: `assertGreater`/`assertFalse`/`assertGreaterEqual` instead of
    boolean `assertTrue` comparisons; redundant try/except removed.

### Added

- **Static-analysis stack** on top of the existing Ruff/mypy/Bandit gates:
  - **Pyright** as a second, blocking type checker (`[tool.pyright]` in
    `pyproject.toml`, `make lint` / `make pyright`, CI `quality` job).
  - **Semgrep** advanced SAST (`p/python` + `p/security-audit`) in the CI
    `security` job and via `make semgrep` (install with
    `pip install -e ".[static]"`).
  - **Gitleaks** secret-scanning job in CI and `make gitleaks`.
  - **CodeQL** workflow (`.github/workflows/codeql.yml`): push/PR plus a
    weekly scheduled deep analysis (`security-extended` queries).
  - **SonarCloud** workflow (`.github/workflows/sonarcloud.yml`) gated on
    the `SONAR_TOKEN` secret, with `sonar-project.properties` (adjust
    `sonar.organization` / `sonar.projectKey` once the project is
    provisioned on SonarCloud).

### Changed

- Codebase made pyright-clean (0 errors / 0 warnings) without inline
  suppressions:
  - New typed helpers `normadocs.utils.docx_helpers`
    (`paragraph_style`, `paragraph_style_name`) narrow python-docx's
    `BaseStyle` lookups and `str | None` style names across the APA,
    ICONTEC, and IEEE formatters and the verifier.
  - `add_tab_stop` now receives `WD_TAB_ALIGNMENT` / `WD_TAB_LEADER`
    enums instead of raw int literals.
  - `lt_client` is explicitly initialized in the CLI (previously possibly
    unbound when LanguageTool post-check ran).
  - Removed the dead `Styles.get_by_name` branch in
    `verifier/docx_analyzer.py` (python-docx has no such method; the
    fallback scan was the real code path).

## [0.2.3] - 2026-08-05

Stable release of the 0.2.3 beta (no code changes since 0.2.3b0; the
beta was promoted to stable after the CI pipeline verified it end to
end). This release fixes 5 APA 7 verifier false-failure paths, tightens
the local quality gates beyond CI, and adds 35 strict unit tests.

### Fixed

- **APA 7 verifier — 5 false-failure corrections** (commit 27c6548):
  - `paragraphs`: filter headings, TOC, abstract, references, captions,
    lists, and "Nota" paragraphs from the first-line-indent count so they
    no longer trigger false `first_line_indent` errors (mirrors the
    formatter's `apply_body_indent` exclusions).
  - `paragraphs`: APA 7 Section 2.21 requires LEFT alignment (ragged
    right), NOT full justification. The verifier now flags justified
    body text and stops flagging left-aligned text.
  - `spacing`: table captions, table titles, and "Nota" paragraphs are
    excluded from the line-spacing check (APA 7 allows single spacing in
    table elements).
  - `references`: hanging indent is `-0.5in` (negative `first_line_indent`
    with positive `left_indent`), not `+0.5in`.
  - `tables`: the italic table title lives in the SEPARATE paragraph
    after the bold "Tabla N" paragraph; the verifier now scans the next
    paragraph for italic instead of expecting it inline.
- Typo fixed in constant name: `EXPECTED_FIRST_LINE_INENT` ->
  `EXPECTED_FIRST_LINE_INDENT`.
- Module docstring corrected (was claiming "Text is justified").
- Type annotation tightened for `mypy --strict` (`filtered: list` ->
  `list[DOCXParagraphInfo]`).
- Verification score on a real document improved from 40.0/100 (FAILED)
  to 89.1/100 (PASSED) with 0 errors.

### Changed

- `Makefile` is now stricter than the CI gates: `ruff check src/ tests/`
  with `RUFF_NOQA=1`, `mypy --strict src/`, `ruff format --check src/
  tests/`, and `pytest -W error --cov-fail-under=86` (CI gate is 78).
- CI workflows bumped `astral-sh/setup-uv@v5` -> `@v8.3.2` to eliminate
  the Node.js 20 deprecation annotation that was failing the
  zero-annotations job across `ci.yml`, `docs.yml`, and `release.yml`.

### Tests

- Added 35 strict unit tests for the APA 7 verifier, lifting overall
  coverage from 82.93% to 86.96%:
  - `TestParagraphsCheckExclusions` (9) + indent branch (1) ->
    `paragraphs.py` 68% -> 100%.
  - `TestSpacingCheckExclusions` (6) + early-return (2) + non-numeric
    spacing (2) -> `spacing.py` 86% -> 100%.
  - `TestReferencesCheckEmptySection` (1) -> `references.py` 94% -> 100%.
  - `TestTablesCheckCaptionItalicSeparateParagraph` (4) + tightening of
    `test_apa_table_proper_caption_passes` to assert
    `warnings == []` -> `tables.py` 100% -> 100% (semantically tightened).
  - `TestAPAVerifierEndToEnd` (4), `TestAPAVerifierReport` (3),
    `TestAPAVerifierDocxDiscovery` (2), `TestAPAVerifierClose` (1) ->
    `apa_verifier.py` orchestrator 24% -> 90%.
- 608 tests pass, 3 skipped, with `-W error`.

## [0.2.2] - 2026-07-08

### Added

- `short_title` field in `DocumentMetadata` for APA 7 running head
- Complete APA 7th Edition documentation (`docs/src/standards/apa7.md`)
- `examples/example_apa.md` - Full APA 7 paper example in English
- Unit tests for `APAPageHandler` (15 tests)
- Unit tests for `APAStylesHandler` (24 tests)
- Running head implementation in `APAPageHandler` (short title uppercase in left header)
- `SUPPORT.md` — how to ask usage questions, report bugs, request features, and
  report security issues.
- `GOVERNANCE.md` — maintainer-led governance model, decision process, and
  roadmap mechanics.
- `MAINTAINERS.md` — current maintainer, responsibilities, and criteria for
  future maintainers.
- `docs/COMMUNITY.md` — community channels and recommended Discussion
  categories.
- `examples/references.bib` — BibTeX example for the BibTeX → CSL → DOCX
  pipeline.
- GitHub labels: `testing`, `ci`, `security`, `formatting-standard`, `icontec`,
  `apa`, `ieee`, `mla`, `windows`, `community`, `roadmap`, `starter`,
  `dependencies`.
- GitHub milestones: `v0.2.2 - Open Source Readiness`,
  `v0.3.0 - Academic Standards Expansion`,
  `v0.4.0 - Community Templates`.
- GitHub Discussions enabled.

### Changed

- Standardized all caption prefixes to English ("Table", "Figure") in APA formatter
- APA 7 documentation now comprehensive with all formatting rules documented
- `apa7.yaml` caption prefixes updated from Spanish to English
- Open-source readiness pass: added root `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `CITATION.cff`, `ROADMAP.md`, `docs/GOOD_FIRST_ISSUES.md`, and
  `.github/ISSUE_TEMPLATE/documentation.yml`. Tightened `SECURITY.md` and the
  pull-request template. Added `Documentation` and `Changelog` URLs to
  `pyproject.toml`.
- README expanded with `What is NormaDocs?`, `Why this exists`,
  `Ecosystem impact`, `Who it is for`, `Project status`, `Citation`, and a
  `Resources` section linking the new governance / support / community files.
- Repository description updated and topics added on GitHub.

### Fixed

- Spanish hardcoding removed from `apa_tables.py` defaults
- `apa_figures.py` now uses `caption_prefix` dynamically from config
- `apa_keywords.py` default `caption_prefix` fixed from "Figura" to "Figure"
- `mypy` strict errors in `src/normadocs/utils/__init__.py` (`__all__` now
  properly annotated as `list[str]`) and `src/normadocs/formatters/ieee.py`
  (table style assignment narrowed via `cast(Any, ...)` with explanation
  comment, no `# type: ignore`).
- README link to contributor docs (was pointing to a non-existent
  `docs/src/contributing.md`; now points to root `CONTRIBUTING.md`).
- OCR lint violations introduced by the OCR integration commit (RUF046, W292
  in `src/normadocs/ocr.py`; I001, SIM117, W292 in `tests/test_ocr.py`).
- mypy `no-any-return` errors in `src/normadocs/ocr.py` (4 occurrences) and
  pre-existing `__all__` / `table.style` annotations in
  `utils/__init__.py` and `formatters/ieee.py`.
- `tests/test_cli.py` updated to work with `typer` 0.26+ / `click` 8.4+
  (replaces `runner.isolated_filesystem()` with `tempfile.TemporaryDirectory()`).
- `tests/test_ocr.py` end-to-end test now auto-skips when `tesseract` is not
  on PATH (`pytest.mark.skipif`).
- `pyproject.toml`: `pytest` `markers` entry registered for the `ocr` mark;
  dev install pinned `numpy>=1.24,<2.5` to avoid a mypy 2.x parser bug
  with numpy 2.5.1 stubs.

### chore

- Excluded `scripts/` directory from ruff linting (utility scripts)
- Fixed lint issues in `test_apa_page.py` and `test_apa_styles.py`
- `make check` is now fully green end-to-end (ruff, ruff format, mypy
  `--strict`, bandit, pytest with `--cov-fail-under=78`).
- Public open-source readiness: lint, type, security, and full test matrix
  (Python 3.10 / 3.11 / 3.12 / 3.13) all green on `main`.

## [0.2.1] - 2026-04-10

### Fixed

- Release workflow PyPI check now properly uses separate job with outputs
- `check-pypi` job correctly passes `already_published` result to `publish` job via job outputs
- `skip_existing: true` in pypa/gh-action-pypi-publish action

## [0.2.0] - 2026-04-10

### Added

- Complete documentation site with Material theme (MkDocs)
- GitHub issue templates (bug_report.yml, feature_request.yml)
- GitHub pull request template
- GitHub CODEOWNERS file
- GitHub SECURITY.md policy
- GitHub Dependabot configuration for automated dependency updates
- GitHub Pages workflow for documentation deployment
- Example documents for ICONTEC and IEEE standards
- Zero Annotations enforcement job in CI workflow
- Annotation validation in release workflow
- Complete CI/CD pipeline setup
- Version validation in release workflow (tag must match pyproject.toml)
- PyPI existence check before upload attempt

### Changed

- Updated all GitHub Actions to latest versions (checkout@v5, setup-python@v6, upload-artifact@v6, download-artifact@v6)
- CI runs with strict linting (`ruff --noqa`, `mypy --strict`)
- Security scanning with Bandit
- Docker cache strategy optimized (`mode=max` to `mode=min`)
- Multi-platform Docker builds (linux/amd64, linux/arm64)
- Improved test coverage with proper mocking of pdf_generator wrappers
- Release workflow refactored with inline CI jobs and quality gates
- PyPI publish action updated to v1.14.0 with `skip_existing: true`

### Fixed

- Empty string split causing errors in cli_helpers.py
- 100-line YAML frontmatter limit removed in preprocessor.py
- Orphan table safety check added in apa_tables.py
- Test mocking properly targets pdf_generator wrappers
- CommandFailedError import missing in tests
- Workflow startup_failure caused by reusable workflow concurrency collision
- Multiple workflows calling same reusable workflow simultaneously
- `.dockerignore` excluding README.md (required by pyproject.toml)
- Docker publish workflow removing redundant CI job

### Removed

- Docker build steps from release.yml (now handled by docker-publish.yml)
- Redundant workflow_call to ci.yml causing matrix expansion conflicts

## [0.1.2a1] - 2025-02-17

### Added

- Initial alpha release
- APA 7th edition formatter
- ICONTEC formatter
- IEEE formatter
- CLI with Typer
- PDF generation with LibreOffice and WeasyPrint

[0.2.2]: https://github.com/CristianMz21/normadocs/releases/tag/v0.2.2
[0.2.1]: https://github.com/CristianMz21/normadocs/releases/tag/v0.2.1
[0.2.0]: https://github.com/CristianMz21/normadocs/releases/tag/v0.2.0
[0.1.2a1]: https://github.com/CristianMz21/normadocs/releases/tag/v0.1.2a1
