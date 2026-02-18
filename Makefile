install:
	pip install -e ".[dev]"

test:
	python3 -m unittest discover tests

lint:
	ruff check .
	mypy src/normadocs

format:
	ruff format .

build:
	python3 -m build

clean:
	rm -rf dist build *.egg-info .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

publish:
	twine upload dist/*
