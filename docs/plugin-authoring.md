# Plugin authoring

Plugins are async handlers registered in `PluginRegistry`. Each plugin declares a stable `name`, semantic `version`, and optional Pydantic `input_model` / `output_model` pair used by `plugins.validation`.

## Lifecycle

1. Implement `Plugin` subclass in `plugins/pack/` or `plugins/extra_plugins.py`.
2. Register inside a `register_*_plugins(registry)` function.
3. Call the register function from `plugins/pack/__init__.py` or from application startup.
4. Add pytest coverage under `tests/test_plugin_pack_*.py`.

## Payload contract

Runtime payloads include:

- `input` — workflow-level input map
- `node` — node definition (id, plugin, input, depends_on)
- `outputs` — upstream node results keyed by node id

Plugins should read explicit fields from the merged payload produced by `WorkflowEngine._merge_payload` and return JSON-serializable dictionaries only.

## Capabilities

Pass capability tags when registering (`registry.register(plugin, capabilities=[...])`). Workflows may declare `requires` on nodes; `WorkflowValidator` ensures the plugin exposes those capabilities.

## Versioning

`PluginRegistry` rejects conflicting versions for the same plugin name. Bump `version` when changing input or output schemas.
