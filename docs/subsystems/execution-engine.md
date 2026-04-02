# Execution engine

`WorkflowEngine` coordinates validation, planning, scheduling, and persistence. The engine is intentionally synchronous by default (`async_mode=False`) so tests remain deterministic; asynchronous scheduling reuses the same node runner with `Scheduler` stage execution.

## Node runner

Each node receives a payload containing workflow input, upstream `outputs`, and the static node definition. Retry policies re-invoke plugins with exponential backoff sleeps. Timeout policies wrap plugin execution with `asyncio.wait_for`.

## Cache integration

`CachePolicy.from_node` reads optional per-node cache configuration. Keys incorporate workflow id, node id, and a stable JSON fingerprint of the payload unless custom key fields are configured.

## Failure semantics

When a node exhausts retries, the engine records a failed log entry and aborts the workflow. Earlier node outputs remain in the database for post-mortem trace and checkpoint inspection.
