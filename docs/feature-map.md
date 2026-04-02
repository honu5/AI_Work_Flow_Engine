# Feature Map

## Plugins

- **Text** — normalize, tokenize, count, replace, n-gram
- **Data** — unique, sort, median, group, map
- **Routing** — switch, fan-out, gate, throttle, merge
- **Validation** — required keys, range, length, contains, email
- **Analysis** — keyword density, numeric profile, list chunking, section indexing
- **Formatting & logic** — join, clamp, boolean helpers
- **Extra bundle** — `plugins/extra_plugins.py` (text stats, reverse)

## Workflow recipes

`workflows/recipes.py` builds composable example workflows:

- Text cleanup pipeline
- Analysis and reporting pipeline
- Validation pipeline
- Routing pipeline

## Catalog

`workflows/catalog/recipes.json` holds curated workflow definitions loaded by `workflows/catalog/loader.py`.

## Documentation

- [architecture.md](architecture.md) — system design
- [development.md](development.md) — local setup and testing
- [operations.md](operations.md) — persistence and observability

## CLI

- `validate` — check workflow JSON against the registry
- `import` / `export` — persist workflows to storage
- `replay`, `logs`, `metrics` — inspect executions
- `register-plugins` — load the extra plugin bundle
