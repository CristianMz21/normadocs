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
	pyright

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

security:
	bandit -r src/normadocs -c pyproject.toml

semgrep:
	SEMGREP_SEND_METRICS=off semgrep scan \
		--config p/python --config p/security-audit --error src/

gitleaks:
	@command -v gitleaks >/dev/null 2>&1 || { \
		echo "gitleaks no está instalado (brew install gitleaks)"; exit 1; }
	gitleaks detect --source . --redact -v

static-analysis: pyright semgrep security gitleaks
	@echo "✅ Static analysis suite passed."

pyright:
	pyright

build:
	python3 -m build

check: lint test-cov security
	@echo "✅ All quality checks passed."

clean:
	rm -rf dist build *.egg-info .mypy_cache .ruff_cache .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +

publish:
	twine upload dist/*
