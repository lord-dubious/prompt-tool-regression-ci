.PHONY: test lint format run

lint:
	uv run --extra dev ruff check src tests

format:
	uv run --extra dev ruff format src tests

test:
	uv run --extra dev pytest tests/ --cov=prompt_tool_regression_ci --cov-report=term-missing

run:
	uv run prompt-tool-regression-ci
