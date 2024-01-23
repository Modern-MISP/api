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

up:
	docker-compose up -d

dev:
	source venv/bin/activate; \
	uvicorn mmisp.api.main:app --reload --port 4000

dev/native:
	uvicorn mmisp.api.main:app --reload --port 4000

print-changes:
	MYSQL_USER=misp MYSQL_PASSWORD=misp MYSQL_HOST=localhost MYSQL_DBNAME=misp python -m mmisp.db.print_changes
