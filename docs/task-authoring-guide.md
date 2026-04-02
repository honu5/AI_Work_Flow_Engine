# Task authoring guide (Silver / Harbor)

This repository is intended as a **real orchestration codebase** for SWE-bench-style tasks. When authoring tasks against AWE, prefer defects and features grounded in git history.

## Picking a base commit

1. Locate a commit that introduces or fixes non-trivial behavior.
2. Set `base_commit` to the parent of that fix (broken state).
3. Ensure the bug is observable through **runtime tests**, not source greps.

## Good task themes in this repo

- **Execution engine** — retry/backoff, cache keys, checkpoint snapshots, timeout handling
- **Workflow validation** — cycles, missing plugins, capability requirements
- **Plugin packs** — transform/aggregate edge cases, validation failures
- **DSL/compiler** — parse errors, dependency ordering, diagnostic messages
- **API contracts** — catalog listing, execution logs, checkpoint endpoints

## Tests

- Add focused pytest cases in `tests/` that fail at `base_commit` and pass after the fix.
- Name tests so Harbor `fail_to_pass` entries match pytest node ids exactly.
- Keep tests behavioral: assert outputs, status codes, and persisted records.

## Instructions

- Describe symptoms and expected outcomes with concrete examples.
- Do not prescribe variable names, file paths for the fix, or pseudocode.
- Reference public API behavior when the agent must discover HTTP or CLI contracts.

## Harness

Run locally before submitting:

```bash
harbor run -p ./my-task -a nop    # must fail
harbor run -p ./my-task -a oracle # must pass
```

## Difficulty

Tasks should require tracing across modules (for example, from API route to registry to engine). Avoid one-line typos unless coupled with subtle runtime effects.
