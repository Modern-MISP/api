SHELL := $(shell which zsh)

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

setup/ci:
	pip install virtualenv; \
	virtualenv venv; \
	source venv/bin/activate; \
	pip install -e ".[dev]"

up:
	docker-compose up -d

dev:
	source venv/bin/activate; \
	uvicorn mmisp.api.main:app --reload --port 4000

dev/native:
	uvicorn mmisp.api.main:app --reload --port 4000

test:
	source venv/bin/activate; \
	ENV_FILE=.env.test python tests/prepare.py; \
	ENV_FILE=.env.test pytest tests

test/lite:
	rm -f mmisp-tests.db; \
	source venv/bin/activate; \
	ENV_FILE=.env.test.lite pytest tests

test/plain:
	pytest tests

print-changes:
	MYSQL_USER=misp MYSQL_PASSWORD=misp MYSQL_HOST=localhost MYSQL_DBNAME=misp python -m mmisp.db.print_changes
