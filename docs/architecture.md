# Architecture

## Overview

AWE executes workflows defined as directed acyclic graphs (DAGs) of plugin nodes. Each node invokes a registered plugin handler; outputs flow to dependent nodes via the execution context. State is persisted for auditing, retries, and API inspection.

## Execution flow

1. **Validate** — `WorkflowValidator` checks node references, cycles, and plugin availability.
2. **Plan** — `ExecutionPlanner` orders nodes topologically and assigns stages.
3. **Schedule** — `Scheduler` runs stages sequentially; nodes within a stage may run concurrently when safe.
4. **Execute** — `WorkflowEngine` invokes plugins, applies retry/timeout policies, writes logs and metrics, and optionally caches node outputs.
5. **Persist** — `Repository` stores workflow definitions, versions, executions, and per-node results.

## Plugin model

Plugins subclass `plugins.base.Plugin` and declare `name`, `version`, and optional capability tags. The `PluginRegistry` enforces unique `(name, version)` pairs and records registration metadata. Plugin packs under `plugins/pack/` group domain handlers (text, data, routing, validation, analysis).

Input payloads include prior node outputs under `outputs` keyed by node id, enabling DAG data flow without global mutable state.

## Storage

SQLAlchemy models cover workflows, versions, executions, plugins, capabilities, and metrics. Tests use ephemeral SQLite databases via `init_db(force=True)`. Production deployments can point `DATABASE_URL` at PostgreSQL or another supported backend.

## API layer

FastAPI routers under `api/routes/` expose workflow CRUD, execution triggers, and plugin discovery. Dependencies in `api/dependencies.py` wire the engine, registry, repository, and cache for each request.

## Expressions

The `workflows/expressions/` package provides a small lexer/parser and evaluator for conditions used in routing and validation scenarios. Tokens cover literals, identifiers, comparisons, and boolean combinators.

## CLI

`cli/main.py` dispatches subcommands implemented in `cli/commands.py`. Import/export round-trips workflow JSON through the same schemas the API uses, keeping local tooling aligned with server behavior.

## Workflow DSL and compiler

The `workflows/dsl/` package implements a small declarative language for workflows (`.wf.dsl` files). The parser produces an AST that compiles into `WorkflowCreate` definitions. `workflows/workflow_compiler.py` layers compile-time diagnostics: topological stages, critical-path extraction, and warnings for overly deep dependency chains.

## Checkpoints

When `checkpoint=True` is passed to `WorkflowEngine.run_workflow`, each successful node persists a serializable snapshot of accumulated outputs via `ExecutionCheckpointRecord`. This supports inspection APIs and future resume strategies without mutating completed node history.

## Scenario library

`workflows/scenarios/builders.py` defines programmatic workflow constructors used in tests and export tooling (`scripts/export_scenarios.py`). Scenarios complement static JSON catalog entries under `workflows/catalog/`.

## Extension guidelines

- Add plugins via `PluginRegistry.register` or new modules in `plugins/pack/`.
- Register built-ins in `plugins/builtin.py` for core handlers.
- Add workflow examples to `workflows/catalog/*.json`, `workflows/scenarios/`, or builders in `workflows/recipes.py`.
- Cover new behavior with pytest cases under `tests/` using fixtures from `conftest.py`.
