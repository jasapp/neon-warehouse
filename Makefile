# neon-warehouse Makefile

.PHONY: help install test lint format clean

help:
	@echo "neon-warehouse - Administrative Assistant Tooling"
	@echo ""
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters (mypy, ruff)"
	@echo "  make format     - Format code with black"
	@echo "  make clean      - Clean build artifacts"
	@echo ""

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

test:
	pytest tests/ -v

lint:
	mypy tools/
	ruff check tools/ tests/

format:
	black tools/ tests/
	ruff check --fix tools/ tests/

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
