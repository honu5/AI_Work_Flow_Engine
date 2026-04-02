# API surface

FastAPI routers are split by resource to keep dependency wiring localized:

| Router | Prefix | Responsibility |
|--------|--------|----------------|
| health | `/health`, `/ready` | Probes |
| catalog | `/catalog` | Template discovery |
| workflows | `/workflows` | CRUD + execute |
| executions | `/executions` | History, logs, trace, checkpoints |
| plugins | `/plugins` | Registry metadata |

Factory creation lives in `api.main.create_app` so tests can inject repositories and engines through dependency overrides.
