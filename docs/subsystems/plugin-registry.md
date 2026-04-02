# Plugin registry

`PluginRegistry` is the runtime lookup table for plugins. Registration persists metadata to SQLite so the API can list plugins and capabilities independently of in-memory instances.

## Validation pipeline

`plugins.validation.validate_input` and `validate_output` coerce payloads through Pydantic models when defined. This keeps HTTP and CLI pathways aligned with engine execution.

## Conflicts

Only one version per plugin name may be active. Attempting to register a second version raises an error, preventing ambiguous handler selection during workflow execution.

## Capability tags

Capabilities are optional strings used by `WorkflowValidator` when nodes declare `requires`. This allows workflows to demand features such as `transform:slugify` without hard-coding plugin names in validation logic.
