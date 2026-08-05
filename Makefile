install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -W error --cov=normadocs --cov-report=term-missing --cov-report=xml --cov-fail-under=86

lint:
	RUFF_NOQA=1 ruff check src/ tests/ --no-cache
	ruff format --check src/ tests/ --no-cache
	mypy --strict src/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

security:
	bandit -r src/normadocs -c pyproject.toml

build:
	python3 -m build

check: lint test-cov security
	@echo "✅ All quality checks passed."

clean:
	rm -rf dist build *.egg-info .mypy_cache .ruff_cache .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +

publish:
	twine upload dist/*
