FROM python:3.11-bookworm AS builder

WORKDIR /build

COPY pyproject.toml .
COPY src src

RUN pip install --no-cache-dir .

FROM python:3.11-bookworm

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/

EXPOSE 4000

ENTRYPOINT uvicorn mmisp.api.main:app --host 0.0.0.0 --port 4000
