# Changelog

All notable changes to **NormaDocs** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Multi-standard architecture with `DocumentFormatter` interface.
- Factory pattern for formatter selection.
- CLI support for multiple citation styles via `--style` flag.
- `--bibliography` and `--csl` CLI flags for Pandoc citation processing.
- APA-style table captions: **Tabla X** (bold) + _Título_ (italic).
- APA-style table borders (horizontal only, no vertical lines).
- `PDFGenerator.convert()` convenience method (LibreOffice → WeasyPrint fallback).
- `py.typed` marker for PEP 561 typed package support.
- Bandit security scanning in CI.
- Coverage reporting with 60% minimum threshold.
- `CONTRIBUTING.md` guidelines.

### Changed

- **BREAKING (CI)**: `release.yml` now requires full CI to pass before publishing.
- **BREAKING (CI)**: `docker-publish.yml` now requires CI to pass before building/pushing.
- Refactored `docx_formatter.py` into separate `formatters/` package.
- `weasyprint` moved from hard dependency to optional `[pdf]` extra.
- Ruff configured with strict lint rules (`E, F, W, I, UP, B, SIM, RUF`).
- MyPy tightened: `check_untyped_defs = true`, `warn_return_any = true`.
- Docker workflow updated from pinned SHAs to latest major action tags.
- Improved test suite to verify full formatting pipeline.

### Fixed

- `p.style.name` null safety guard in `apa.py` and `icontec.py`.
- B904: `raise ... from None` in CLI exception handlers.
- SIM102: Simplified nested `if` in APA body text formatting.
- All deprecated `typing.List/Dict/Tuple/Optional` replaced with modern syntax.
- Import sorting enforced across all modules and tests.

## [0.1.2a1] - 2026-02-18

### Fixed

- Reordered `pyproject.toml` tables to fix build errors with `hatchling`.
- Resolved `[project.urls]` table placement issue preventing build.

## [0.1.1a1] - 2026-02-18

### Changed

- Initial PyPI release under new name **NormaDocs**.
- Renamed project from APAScript.
- Updated documentation and branding.

## [0.1.0] - 2023-01-01

### Added

- Basic Markdown to DOCX conversion.
- Initial support for APA 7th Edition formatting.
- `pandoc` integration for conversion.
- PDF generation via LibreOffice or WeasyPrint fallback.
