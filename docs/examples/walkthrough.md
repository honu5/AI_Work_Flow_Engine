# End-to-end walkthrough

This walkthrough exercises the engine without Docker, using pytest fixtures as a guide for manual exploration.

## 1. Create a workflow via JSON

```json
{
  "name": "adder_flow",
  "nodes": [
    {"id": "sum", "plugin": "add_numbers", "input": {"a": 10, "b": 32}}
  ]
}
```

Import through the CLI:

```bash
python -m cli.main import examples/echo_pipeline.json
```

## 2. Compile from DSL

`examples/onboarding.wf.dsl` demonstrates dependency syntax:

```bash
python -m cli.main compile-dsl examples/onboarding.wf.dsl
```

## 3. Inspect catalog templates

```bash
python -m cli.main catalog-summary
```

Templates include operational scenarios such as `incident_triage`, `fraud_scoring`, and exported programmatic scenarios under `workflows/catalog/generated/`.

## 4. Execute with checkpoints

When calling the engine programmatically, pass `checkpoint=True` to persist per-node snapshots. List them with:

`GET /executions/{execution_id}/checkpoints`

## 5. Review traces

After a run completes, fetch:

`GET /executions/{execution_id}/trace`

The response summarizes plugins used, per-node status, and elapsed time derived from execution logs.

## 6. Validate before deploy

```bash
python -m cli.main validate examples/text_pipeline.json
python -m cli.main describe-workflow examples/text_pipeline.json
```

`describe-workflow` returns compile diagnostics including stages and critical path nodes.

## 7. Batch-run catalog samples

```bash
python -m cli.main batch-catalog --limit 3
```

Use this for smoke testing after plugin or engine changes.

## 8. Scenario builders

```python
from workflows.scenarios.builders import build_document_ingest
workflow = build_document_ingest()
```

Scenario builders are the preferred way to add complex DAGs in tests because they stay type-checked and composable.

## 9. Adding a plugin

1. Create a handler in `plugins/pack/`.
2. Register it in the pack `register_*` function.
3. Add pytest coverage in `tests/test_plugin_pack_*.py`.
4. Reference the plugin from a catalog JSON or scenario builder.

## 10. Authoring Silver tasks

See `docs/task-authoring-guide.md` for constraints on tests, instructions, and difficulty.
