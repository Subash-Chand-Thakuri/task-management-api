# `app/models/` — Database Models

ORM model classes that map directly to database tables.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package marker. Import all models here so Alembic can discover them. |
| `user.py` | `User` model with `id`, `email`, and `is_active` columns. |

## Notes

- Models import `Base` from `app.db.base` — make sure every new model does the same.
- To add a new model, create a file (e.g. `item.py`), define the class, then import it in `__init__.py`.
