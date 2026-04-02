# Operations

## Persistence

Workflow definitions, execution records, plugin registrations, and per-node metrics are stored through `storage/repository.py`. The default configuration uses SQLite; set `DATABASE_URL` before calling `init_db()` for other backends.

## Observability

- Execution logs: per-node status transitions and errors
- Metrics: duration and attempt counts per node
- CLI: `logs` and `metrics` subcommands read the same repository tables as the API

## Container image

The root `Dockerfile` installs pinned dependencies from `requirements.txt` and runs `pytest -q` as the default command for Silver repository validation builds.
