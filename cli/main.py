from __future__ import annotations

import argparse
import json
from pathlib import Path

import asyncio

from api.dependencies import get_engine, get_registry, get_repository
from cli.batch import run_catalog_subset_sync
from cli.commands import (
    cli_register_extra_plugins,
    export_logs,
    export_metrics,
    export_workflow,
    import_workflow,
    load_workflow,
    replay_execution,
    validate_workflow,
)
from cli.inspect import catalog_summary, describe_plugin, describe_workflow, format_json, list_registered_plugins
from workflows.dsl import compile_dsl


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="awe")
    sub = parser.add_subparsers(dest="command", required=True)

    validate_cmd = sub.add_parser("validate", help="Validate a workflow JSON file")
    validate_cmd.add_argument("path")

    import_cmd = sub.add_parser("import", help="Import a workflow JSON file")
    import_cmd.add_argument("path")

    export_cmd = sub.add_parser("export", help="Export a workflow JSON file")
    export_cmd.add_argument("workflow_id")
    export_cmd.add_argument("output")

    replay_cmd = sub.add_parser("replay", help="Replay an execution")
    replay_cmd.add_argument("execution_id")

    logs_cmd = sub.add_parser("logs", help="Export execution logs")
    logs_cmd.add_argument("execution_id")

    metrics_cmd = sub.add_parser("metrics", help="Export execution metrics")
    metrics_cmd.add_argument("execution_id")

    register_cmd = sub.add_parser("register-plugins", help="Register extra sample plugins into the registry")

    inspect_cmd = sub.add_parser("inspect-plugin", help="Show plugin metadata")
    inspect_cmd.add_argument("name")

    catalog_cmd = sub.add_parser("catalog-summary", help="Summarize workflow catalog templates")

    compile_cmd = sub.add_parser("compile-dsl", help="Compile workflow DSL file to JSON")
    compile_cmd.add_argument("path")

    describe_cmd = sub.add_parser("describe-workflow", help="Compile and describe a workflow JSON file")
    describe_cmd.add_argument("path")

    batch_cmd = sub.add_parser("batch-catalog", help="Execute first N catalog templates")
    batch_cmd.add_argument("--limit", type=int, default=3)

    sub.add_parser("doctor", help="Run project health checks")

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    repository = get_repository()
    registry = get_registry()
    engine = get_engine()

    if args.command == "validate":
        payload = load_workflow(Path(args.path))
        errors = validate_workflow(payload, registry)
        print(json.dumps({"errors": errors}))
        return

    if args.command == "import":
        payload = load_workflow(Path(args.path))
        workflow_id = import_workflow(repository, payload)
        print(json.dumps({"workflow_id": workflow_id}))
        return

    if args.command == "export":
        export_workflow(repository, args.workflow_id, Path(args.output))
        print(json.dumps({"workflow_id": args.workflow_id, "output": args.output}))
        return

    if args.command == "replay":
        result = asyncio.run(replay_execution(engine, repository, args.execution_id))
        print(json.dumps({"status": result.status.value, "output": result.output}))
        return

    if args.command == "logs":
        logs = export_logs(repository, args.execution_id)
        print(json.dumps({"logs": logs}))
        return

    if args.command == "metrics":
        metrics = export_metrics(repository, args.execution_id)
        print(json.dumps({"metrics": metrics}))
        return

    if args.command == "register-plugins":
        cli_register_extra_plugins(registry)
        print(json.dumps({"registered": True}))
        return

    if args.command == "inspect-plugin":
        print(format_json(describe_plugin(registry, args.name)))
        return

    if args.command == "catalog-summary":
        directory = Path(__file__).resolve().parents[1] / "workflows" / "catalog"
        print(format_json(catalog_summary(directory)))
        return

    if args.command == "compile-dsl":
        text = Path(args.path).read_text(encoding="utf-8")
        workflow = compile_dsl(text)
        print(json.dumps(workflow.model_dump(), indent=2))
        return

    if args.command == "describe-workflow":
        payload = load_workflow(Path(args.path))
        print(format_json(describe_workflow(payload, registry)))
        return

    if args.command == "doctor":
        from cli.doctor import run_doctor

        print(format_json(run_doctor()))
        return

    if args.command == "batch-catalog":
        directory = Path(__file__).resolve().parents[1] / "workflows" / "catalog"
        rows = run_catalog_subset_sync(engine, repository, directory, limit=args.limit)
        print(json.dumps({"results": rows}))
        return


if __name__ == "__main__":
    main()
