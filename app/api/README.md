# `app/api/` — API Routes

All HTTP endpoint definitions live here, organised by API version.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Creates the top-level `api_router` and includes versioned sub-routers. |
| `deps.py` | Shared **dependencies** — e.g. `get_current_user` — injected into route handlers via `Depends()`. |

## Sub-packages

| Folder | Description |
|--------|-------------|
| `v1/` | Version 1 endpoints. Add `v2/`, `v3/`, etc. as needed. |
