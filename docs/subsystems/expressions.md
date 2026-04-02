# Expression language

The expression package under `workflows/expressions/` powers conditional logic in advanced workflows. Lexer tokens include identifiers, numbers, strings, comparison operators, and function calls.

## Evaluation model

`Evaluator` walks the AST produced by `ExpressionParser`. Callers may inject a function map for domain-specific helpers; tests use small lambdas to avoid name clashes with Python builtins.

## Error handling

`ExpressionError` surfaces parse failures with human-readable messages. Invalid tokens or unmatched parentheses fail fast during parsing rather than at evaluation time.
