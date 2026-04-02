# Repository submission checklist

- Zip includes the full `.git` directory (required for task base commits).
- Root `Dockerfile` uses a pinned Python image and `requirements.txt`.
- `.dockerignore` excludes caches but not `.git`.
- Run `pytest -q` locally or rely on platform CI before task authoring.
