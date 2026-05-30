# `app/services/` — Business Logic

The service layer keeps route handlers thin by encapsulating business rules and data access.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package marker. |
| `user_service.py` | `get_dummy_users()` — returns sample user data. Replace with real DB queries. |

## Guidelines

- Each service should focus on a **single resource** or **domain concept**.
- Services receive a database session (from `app.db.session.get_session`) and return schema objects.
