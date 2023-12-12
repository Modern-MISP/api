install:
	pip install '.[dev]'

setup:
	virtualenv venv; \
	source ./venv/bin/activate; \
	pip install '.[dev]'

dev:
	source ./venv/bin/activate; \
	uvicorn app.main:app --reload --port 4000

dev/native:
	uvicorn app.main:app --reload --port 4000
