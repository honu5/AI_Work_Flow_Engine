class WorkflowValidationError(ValueError):
    pass


class PluginNotFoundError(LookupError):
    pass


class ExecutionError(RuntimeError):
    pass
