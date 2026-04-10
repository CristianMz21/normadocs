# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-04-10

### Added
- Full documentation site with Material theme (mkdocs)
- GitHub issue templates (bug_report.yml, feature_request.yml)
- GitHub PR template
- GitHub CODEOWNERS
- GitHub SECURITY.md
- GitHub Dependabot configuration
- GitHub Pages workflow for documentation deployment
- Examples for ICONTEC and IEEE standards
- Zero Annotations enforcement job in CI
- Annotation validation in release workflow
- Complete project setup with CI/CD pipelines

### Changed
- CI workflow updated to Node.js 24 compatible actions
- All GitHub Actions updated to latest versions (checkout@v5, setup-python@v6, upload-artifact@v6)
- CI runs with strict linting (ruff --noqa, mypy --strict)
- Security scanning with Bandit
- Docker cache strategy optimized (mode=max to mode=min)
- Multi-platform Docker builds (linux/amd64, linux/arm64)
- Improved test coverage with proper mocking

### Fixed
- Fixed empty string split causing errors in cli_helpers.py
- Removed 100-line YAML frontmatter limit in preprocessor.py
- Added orphan table safety check in apa_tables.py
- Test mocking properly targets pdf_generator wrappers
- CommandFailedError import missing in tests
- Workflow startup_failure caused by reusable workflow concurrency collision
- Multiple workflows calling same reusable workflow simultaneously

### Removed
- Docker build steps from release.yml (now handled by docker-publish.yml)
- Redundant workflow_call to ci.yml causing conflicts

## [0.1.2a1] - 2025-02-17

### Added
- Initial alpha release
- APA 7th edition formatter
- ICONTEC formatter
- IEEE formatter
- CLI with typer
- PDF generation with LibreOffice and WeasyPrint
