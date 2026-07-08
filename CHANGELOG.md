# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### chore

- Excluded `scripts/` directory from ruff linting (utility scripts)
- Fixed lint issues in `test_apa_page.py` and `test_apa_styles.py`
- `make check` is now fully green end-to-end (ruff, ruff format, mypy
  `--strict`, bandit, pytest with `--cov-fail-under=78`).

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

[0.2.1]: https://github.com/CristianMz21/normadocs/releases/tag/v0.2.1
[0.2.0]: https://github.com/CristianMz21/normadocs/releases/tag/v0.2.0
[0.1.2a1]: https://github.com/CristianMz21/normadocs/releases/tag/v0.1.2a1
