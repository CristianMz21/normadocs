# Contributing to NormaDocs

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/CristianMz21/normadocs.git
cd normadocs
pip install -e ".[dev]"
```

## Quality Standards

All contributions must pass:

```bash
make check  # lint + tests + coverage
```

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
