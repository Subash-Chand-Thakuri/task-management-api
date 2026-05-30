# `app/api/v1/` — Version 1 Endpoints

Each file in this folder is a **router module** for a single resource.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package marker. |
| `users.py` | `GET /users/` — returns a list of users. Add more CRUD routes here. |

## Adding a new resource

1. Create a new file, e.g. `items.py`, with its own `router = APIRouter(...)`.
2. Import and include it in `app/api/__init__.py`:
   ```python
   from .v1 import items
   api_router.include_router(items.router)
   ```
