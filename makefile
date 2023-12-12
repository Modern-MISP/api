install:
	pip install ".[dev]"

prepare:
	pre-commit install --install-hooks

setup:
	virtualenv venv; \
	source ./venv/bin/activate; \
	pip install ".[dev]"; \
	pre-commit install --install-hooks

dev:
	source ./venv/bin/activate; \
	uvicorn app.main:app --reload --port 4000

dev/native:
	uvicorn app.main:app --reload --port 4000
