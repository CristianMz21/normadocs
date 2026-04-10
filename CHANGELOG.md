# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.2.0]: https://github.com/CristianMz21/normadocs/releases/tag/v0.2.0
[0.1.2a1]: https://github.com/CristianMz21/normadocs/releases/tag/v0.1.2a1
