# AI Agent Guide for This Repository

This file defines the coding-agent reference for this specific project only.

## Agent Operating Mode

- Be deterministic: prefer explicit commands, explicit paths, and explicit expected outcomes.
- Make minimal changes: avoid unrelated refactors when implementing a request.
- Keep behavior stable unless the task explicitly requests behavior changes.
- After edits, always run validation commands and report outcomes.

## Scope

- Project: Fibonacci Sequence API
- Runtime: Python 3.12, FastAPI
- Source root: `src/`
- Main app entry: `src.app.main:app`

## Current Project Layout

```text
src/
  app/
    main.py
    router.py
    constants.py
    fibonacci.py
    helper/
      exception_handlers.py
      logging_helper.py
      landing_page.py
tests/
  test_api.py
```

## Reproducible Local Setup

Run these commands from the repository root in order:

```bash
uv sync --all-groups
```

## Reproducible Run and Test

Use these exact commands:

```bash
# start API
uv run uvicorn src.app.main:app --reload

# run tests
uv run pytest -q
```

Expected test result baseline:

- All tests in `tests/test_api.py` pass.
- Command exits with code 0.

## Architecture Rules

- Keep API route handlers in `src/app/router.py` unless a new domain module is introduced.
- Keep cross-cutting concerns under `src/app/helper/`:
  - exception handling
  - request logging
  - static landing HTML content
- Keep app bootstrap and wiring in `src/app/main.py` via `create_app()`.
- Keep service constants in `src/app/constants.py`.

## API Contract Rules

- Endpoint: `GET /fibonacci?n=<int>`
- Guardrail: max allowed `n` is defined by `MAX_N`.
- Error responses use the custom JSON envelope from the exception handlers:

```json
{
  "error": {
    "type": "...",
    "message": "...",
    "path": "..."
  }
}
```

- Do not revert to default FastAPI `detail` format unless tests and docs are intentionally updated.

## Change Workflow (Required)

For every code change, follow this sequence:

1. Read affected modules first.
2. Apply the smallest possible patch.
3. Run tests: `uv run pytest -q`.
4. If API behavior changed, update `README.md` endpoint/behavior docs.
5. Summarize exactly what changed and why.

## Commands

- Run locally:
  - `uv run uvicorn src.app.main:app --reload`
- Run tests:
  - `uv run pytest -q`
- Docker build:
  - `docker build -t fibonacci-api .`

## Definition of Done

A task is complete only if all are true:

1. Code compiles/lints cleanly in edited files.
2. Tests pass (`uv run pytest -q`).
3. Imports and module paths remain valid for `src/` layout.
4. README is updated when user-facing behavior/commands changed.
5. No unrelated files were modified.

## Testing Expectations

- Any endpoint behavior change should include test updates in `tests/test_api.py`.
- Keep existing coverage for:
  - health endpoint
  - Fibonacci happy paths
  - invalid input and boundary conditions

## Documentation Expectations

- Keep `README.md` aligned with actual runtime paths and endpoints.
- If docs configuration changes (Swagger/ReDoc/OpenAPI paths), update the endpoint list in `README.md`.

## Out of Scope for This Repo

Avoid introducing unrelated framework guidance unless required by a new feature:

- SQLAlchemy/Alembic/database migration guidance
- JWT/auth framework patterns
- Celery/background job architecture
- Multi-domain microservice conventions

Add those only when the codebase actually includes them.
