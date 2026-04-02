# HTTP API guide

Base application: `api.main:create_app`.

## Health

- `GET /health` — liveness probe
- `GET /ready` — readiness probe (repository + registry reachable)

## Catalog

- `GET /catalog/templates` — list curated workflow templates
- `GET /catalog/templates/{name}` — template detail with compile diagnostics

## Workflows

- `POST /workflows/` — create workflow
- `GET /workflows/{id}` — fetch workflow
- `GET /workflows/` — list workflows (optional `name`, pagination)
- `GET /workflows/{id}/versions` — list versions
- `POST /workflows/{id}/execute` — run workflow (`input`, `async_mode`)

## Executions

- `GET /executions/{id}` — execution detail with logs
- `GET /executions/` — filter by workflow or status
- `GET /executions/{id}/logs` — node logs
- `GET /executions/{id}/checkpoints` — incremental checkpoint snapshots

## Plugins

- `GET /plugins/` — list registered plugins
- `GET /plugins/{name}` — plugin metadata and capabilities
