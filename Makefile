install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=normadocs --cov-report=term-missing --cov-fail-under=60

lint:
	ruff check .
	ruff format --check .
	mypy src/normadocs

format:
	ruff format .
	ruff check --fix .

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
