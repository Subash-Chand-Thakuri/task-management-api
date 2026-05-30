# `app/schemas/` — Pydantic Schemas

Data-validation and serialisation models used in request bodies and responses.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package marker. |
| `user.py` | `User` schema with `id`, `email`, and `is_active` fields. |

## Conventions

- **One file per resource** (e.g. `user.py`, `item.py`).
- Use `Create`, `Update`, and `Read` suffixes when you need separate shapes for different operations, e.g. `UserCreate`, `UserRead`.
