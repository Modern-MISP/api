FROM python:3.11-bookworm AS builder

WORKDIR /build

COPY pyproject.toml .

RUN pip install --no-cache-dir .

FROM python:3.11-bookworm

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/

COPY app app

EXPOSE 4000

ENTRYPOINT uvicorn app.main:app --port 4000
