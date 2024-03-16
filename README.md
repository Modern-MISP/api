# Modern MISP - API

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Conventional Commits](https://img.shields.io/badge/Conventional_Commits-1.0.0-orange.svg)](https://conventionalcommits.org)

## Requirements

- [Docker](https://www.docker.com) `latest-stable`

## Getting Started

Clone the project and install Python version `3.11.0`. It is recommended to install Python using [pyenv](https://github.com/pyenv/pyenv#installation). Then install all dependencies by typing `make setup` into your terminal and start your local database container using `make up`.

Create a file called `.env` and copy the contents of `.env.example` into it. Finally, start the development server using `make dev`.

You should now be able to access the api on `localhost:4000`.

Run tests using `make test` (local database container required running) or `make test/lite`.

## Setting up your IDE

Be sure to use the newly created virtual env as your interpreter (`./venv/bin/python`). Also install the [Ruff](https://docs.astral.sh/ruff/integrations/) extension for your IDE and set `Ruff` as your default code formatter. It is recommended to activate formatting your code on every save.

## Best Practices

### General Guidelines

The following are some guidelines for writing code, in no particular order:

- Try to write clean code
- Use the "early return" pattern, do you really need that `else` block?
- Add correct types wherever possible, reduce `Any` occurrences as much as possible
- Reduce database calls
- Be consistent within your code, and within the rest of the codebase
- Use whitespace generously, to group and separate lines of code
- Be explicit, magic is great until it is not

### Endpoint Ordering

Try to order endpoints using CRUD so that the following order is achieved:

- Create a {resource}
- Read / Get a {resource}
- Update a {resource}
- Delete a {resource}
- Get all {resource}s
- More niche endpoints
- Deprecated endpoints
