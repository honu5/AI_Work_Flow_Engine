# Storage layer

AWE uses SQLAlchemy models mapped to SQLite by default. `Repository` encapsulates CRUD for workflows, versions, executions, logs, metrics, plugins, and checkpoints.

## Schema highlights

- `workflows` stores JSON definitions for DAG templates.
- `workflow_versions` keeps historical snapshots per workflow id.
- `executions` tracks status transitions and serialized results.
- `execution_logs` stores per-node output and errors.
- `execution_checkpoints` stores incremental snapshots when enabled.

## Testing

Pytest fixtures call `init_db(force=True)` with temporary database paths to isolate tests. Never point tests at a production database file.
