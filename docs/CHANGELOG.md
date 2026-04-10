# Changelog

All notable changes to **NormaDocs** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-04-10

### Added

- **Complete docstring audit** - All modules now have Google-style docstrings
- **IEEE 8th Edition formatter** - Full implementation with Times New Roman 10pt, single spacing
- **Multi-standard architecture** - DocumentFormatter interface with factory pattern
- **CLI reference documentation** - Complete --help documentation
- **Troubleshooting guide** - Common issues and solutions
- **Example documents** - APA, ICONTEC, IEEE templates
- **MkDocs documentation site** - Material theme with full navigation
- **GitHub issue/PR templates** - Bug reports and feature requests
- **Security policy** - SECURITY.md with reporting guidelines
- **Dependabot configuration** - Automated dependency updates
- **CODEOWNERS** - Clear code ownership

### Changed

- **CI/CD workflow** - Stricter quality gates (mypy --strict, ruff with no noqa)
- **Docker workflow** - Multi-architecture support (amd64/arm64), version tagging
- **Release workflow** - Fixed OIDC trusted publishing, tag-based triggers
- **Coverage requirement** - Increased from 60% to 78%
- **All subprocess calls** - Centralized via utils/subprocess.py wrapper

### Fixed

- Empty string split filter in LanguageTool rules
- Bare except Exception to specific exception types
- YAML frontmatter 100-line hard limit removed
- Orphaned table element safety check

### Documentation

- API reference documentation
- Library usage guide
- Standard configuration references (APA7, ICONTEC, IEEE)
- Contributing guidelines

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
