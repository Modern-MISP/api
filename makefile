install:
	pip install -e ".[dev]"

prepare:
	pre-commit install --install-hooks

setup:
	pip install virtualenv; \
	virtualenv venv; \
	source venv/bin/activate; \
	pip install -e ".[dev]"; \
	pre-commit install --install-hooks

dev:
	source venv/bin/activate; \
	uvicorn mmisp.api.main:app --reload --port 4000

dev/native:
	uvicorn mmisp.api.main:app --reload --port 4000
