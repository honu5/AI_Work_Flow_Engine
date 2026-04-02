# Workflow graph algorithms

`WorkflowGraph` implements DAG utilities used by validation and compilation:

- Cycle detection via topological sort length comparison
- Levelization for stage-based scheduling
- Critical-path reconstruction using dynamic programming over dependencies

These utilities are shared between `WorkflowValidator` and `compile_workflow` so API diagnostics match engine scheduling constraints.
