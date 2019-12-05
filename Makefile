.PHONY: fmt lint test

fmt:
	poetry run black .

lint:
	poetry run mypy --config-file pyproject.toml .
