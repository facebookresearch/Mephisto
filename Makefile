.PHONY: fmt lint test web

fmt:
	poetry run black .

lint:
	poetry run mypy --config-file pyproject.toml .

web:
	cd mephisto/webapp && npm run build
