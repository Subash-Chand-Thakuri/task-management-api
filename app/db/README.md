# `app/db/` — Database Configuration

Everything related to the database connection, session management, and ORM base class.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package marker. |
| `base.py` | Declares the ORM `Base` class that all models inherit from. |
| `session.py` | Creates the database `engine`, and exposes `get_session()` — a FastAPI dependency that yields a database session. |

## Usage

Inject a session into any route:
```python
from fastapi import Depends
from app.db.session import get_session

@router.get("/")
def list_items(session = Depends(get_session)):
    ...
```
