# Execution model

## Planning

`ExecutionPlanner` builds a DAG plan from workflow nodes. `WorkflowGraph` validates acyclic dependencies, computes topological levels, and exposes critical-path analysis used by `workflows/workflow_compiler.py`.

## Running nodes

`WorkflowEngine.run_workflow` creates an execution record, builds an `ExecutionContext`, and executes nodes either sequentially (`async_mode=False`) or via `Scheduler` stages (`async_mode=True`).

For each node the engine:

1. Builds a payload with workflow input, upstream outputs, and node metadata
2. Applies cache policy when configured
3. Invokes `PluginRegistry.run` with retry and timeout policies
4. Records logs and metrics in SQLite via `Repository`

## Checkpoints

Pass `checkpoint=True` to `run_workflow` to persist incremental output snapshots after each successful node. Checkpoints are stored in `execution_checkpoints` and exposed through the executions API.

## Failure handling

Unhandled plugin errors mark the node log as failed, respect retry/backoff settings, and transition the execution to `failed` without partial result persistence unless earlier nodes completed.
