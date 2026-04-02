# Development

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run tests

```bash
pytest -q
```

## Run API locally

```bash
uvicorn api.main:create_app --factory --reload
```

The factory entrypoint is `create_app()` in `api/main.py`.
