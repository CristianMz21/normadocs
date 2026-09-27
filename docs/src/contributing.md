# Contributing to NormaDocs

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/CristianMz21/normadocs.git
cd normadocs
pip install -e ".[dev]"
```

## Quality Standards

All contributions must pass (see the full checklist in
[CONTRIBUTING.md](https://github.com/CristianMz21/normadocs/blob/main/CONTRIBUTING.md)):

```bash
make check  # lint (ruff + mypy --strict + pyright) + tests + security
```

Rules that bite: no `# noqa` / `# type: ignore` / `# nosec` suppressions
(CI sets `RUFF_NOQA=1` and fails on any annotation), tests run with
`-W error` and `--cov-fail-under=78`. Validate feature branches locally
before pushing — CI runs the full gates only on pull requests to `main`.

## Code Style

- Python 3.10+
- Google-style docstrings
- Type hints required
- 100 character line length

## Testing

```bash
make test        # Run tests
make test-cov    # With coverage
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all checks pass
5. Submit a pull request
