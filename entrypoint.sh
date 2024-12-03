#!/bin/sh


[ -n "${SETUP_DB}" ] && mmisp-db setup --create_init_values=False

gunicorn mmisp.api.main:app -b 0.0.0.0:4000 -w 4 -k uvicorn_worker.UvicornWorker
