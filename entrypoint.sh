#!/bin/sh


[ -n "${SETUP_DB}" ] && mmisp-db setup --create_init_values=False
[ -z "${WORKER_COUNT}" ] && WORKER_COUNT=4

gunicorn mmisp.api.main:app -b 0.0.0.0:4000 -w "$WORKER_COUNT" -k uvicorn_worker.UvicornWorker
