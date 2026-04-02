# AI Workflow Automation Engine

AWE is a local-first workflow orchestration engine for composing and running plugin-based DAGs. It provides a FastAPI surface, SQLAlchemy persistence, deterministic execution with retries and caching, and a CLI for import/export and inspection.

## Features

- **Workflow engine** — topological execution, per-node retries, timeouts, and execution history
- **Plugin system** — versioned handlers with capability metadata and input validation
- **Expression language** — conditional logic for routing and validation nodes
- **Workflow DSL** — compile `.wf.dsl` files into workflow definitions (`workflows/dsl/`)
- **Workflow compiler** — stage planning, critical-path analysis, diagnostics
- **Execution checkpoints** — optional per-node snapshots for long-running DAGs
- **Transform & aggregate plugin packs** — data shaping and summarization handlers
- **Job queue & worker pool** — prioritized async execution with cancellation
- **REST API** — workflows, executions, plugins, health, and catalog endpoints
- **CLI** — validate, import/export, DSL compile, catalog batch runs, inspection helpers

## Architecture

| Layer | Responsibility |
|-------|----------------|
| `api/` | FastAPI routes and dependency wiring |
| `workflows/` | Schemas, DAG validation, recipes, catalog loader, expressions |
| `execution/` | Scheduler, planner, engine, queue, worker pool |
| `plugins/` | Registry, discovery, built-ins, and domain plugin packs |
| `storage/` | SQLAlchemy models and repository |
| `cache/` | Pluggable node output cache |
| `cli/` | Command-line tools |

See [docs/architecture.md](docs/architecture.md) for execution flow, data model, and extension points. See [docs/development.md](docs/development.md) for local setup and test commands.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

Docker (used by Silver repository submission):

```bash
docker build -t awe .
docker run --rm awe
```

## Project layout

- `api/` — HTTP API
- `execution/` — orchestration runtime
- `workflows/` — workflow definitions, validation, recipes, catalog
- `plugins/` — plugin interface and packs (text, data, routing, validation, analysis)
- `storage/` — persistence
- `cache/` — caching
- `cli/` — CLI entrypoints
- `tests/` — pytest suite (API, engine, plugins, expressions, CLI)
- `examples/` — sample workflow JSON for manual import
- `docs/` — architecture and feature notes

## Testing

The suite uses pytest and pytest-asyncio. Coverage includes workflow validation, multi-node DAG execution, cache policies, retry behavior, plugin packs, expression parsing, API contracts, and CLI import/export flows.
