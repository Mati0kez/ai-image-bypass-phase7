.PHONY: install install-dev test lint format clean experiment help

help:
	@echo "AI Image Bypass - Available commands:"
	@echo "  make install      Install package (core dependencies)"
	@echo "  make install-dev  Install with dev dependencies"
	@echo "  make test         Run pytest"
	@echo "  make lint         Run ruff + black check"
	@echo "  make format       Auto-format with black + ruff --fix"
	@echo "  make experiment   Run benchmark in experiment mode (mock)"
	@echo "  make clean        Remove build artifacts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	PYTHONPATH=src ./venv/bin/python -m pytest tests/ -v --tb=short -k "not lpips"

lint:
	ruff check src/ tests/
	black --check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

experiment:
	PYTHONPATH=src benchmark --mode=experiment --platforms remote:mock --samples 10 --output-dir experiment_demo

full-test: test
	@echo "full-test: same as make test until integration tests are added (Phase 7 P1+)"

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
