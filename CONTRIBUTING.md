# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Code style

- Match existing module layout and typing conventions.
- Prefer behavioral pytest coverage for new plugins and API routes.
- Avoid generated copy-paste modules; add reusable builders or packs instead.

## Pull request checklist

- [ ] Tests pass locally (`pytest -q`)
- [ ] New plugins include input/output models and pack registration
- [ ] API changes documented in `docs/api-guide.md`
- [ ] No artificial size-padding files or repetitive scaffold directories
