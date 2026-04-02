# Changelog

## Unreleased

### Added

- Workflow DSL parser and compiler (`workflows/dsl/`)
- Workflow compile diagnostics and critical-path analysis
- Execution checkpoints with REST listing endpoint
- Transform and aggregate plugin packs
- Programmatic scenario builders and catalog export script
- Health and catalog API routes
- CLI inspect, DSL compile, and catalog batch commands
- Execution trace summarization utilities

### Fixed

- Echo plugin now returns serializable payloads without circular references
- Test harness registers full plugin pack during pytest runs
