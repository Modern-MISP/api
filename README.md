# Modern MISP - API

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Conventional Commits](https://img.shields.io/badge/Conventional_Commits-1.0.0-orange.svg)](https://conventionalcommits.org)

## Requirements

- [Docker](https://www.docker.com) `latest-stable`

## Getting started

Clone the project and install Python version `3.11.0`. It is recommended to install Python using [pyenv](https://github.com/pyenv/pyenv#installation). Then install all dependencies by typing `make setup` into your terminal and start your local database container using `make up`.

Create a file called `.env` and copy the contents of `.env.example` into it. Finally, start the development server using `make dev`.

You should now be able to access the api on `localhost:4000`.

## Setting up your IDE

Be sure to use the newly created virtual env as your interpreter (`./venv/bin/python`). Also install the [Ruff](https://docs.astral.sh/ruff/integrations/) extension for your IDE and set `Ruff` as your default code formatter. It is recommended to activate formatting your code on every save.

## Best practices

### Endpoint ordering

Try to order endpoints using CRUD so that the following order is achieved:

- Creatte a {resource}
- Read / Get a {resource}
- Updating a {resource}
- Deleting a {resource}
- Get all {resource}s
- More niche endpoints
- Deprecated endpoints
