# task-management-api

We can scaffold a similar `app/` project in two ways:

**fastapi-easy-setup** (uv-based, fixed production layout — Alembic, async DB, Python 3.12+):

```bash
uvx fastapi-easy-setup task-management-api
cd task-management-api
uv run uvicorn app.main:app --reload
```

**fastapi-initializer** (interactive: DB, ORM, Docker, linter, tests, etc., Python 3.10+):

```bash
uv tool install fastapi-initializer
fastapi-init task-management-api
cd task-management-api
uv sync
uv run uvicorn app.main:app --reload
```

This project was generated with **FastAPI Initializer** (PostgreSQL, SQLAlchemy, Ruff, Docker). The layout below matches that scaffold, not fastapi-easy-setup.

## Getting Started

```bash
# Install dependencies
uv sync

# Run the development server
uv run uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** to explore the interactive API documentation.

## Project Structure

```
task-management-api/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   └── users.py        # User endpoints
│   │   ├── __init__.py          # Mounts versioned routers
│   │   └── deps.py              # Shared dependencies
│   ├── core/
│   │   ├── config.py            # App settings (pydantic-settings)
│   │   └── security.py          # OAuth2 / auth utilities
│   ├── models/
│   │   └── user.py            # ORM model
│   ├── db/
│   │   ├── base.py             # ORM Base class
│   │   └── session.py          # Engine & get_session()
│   ├── schemas/
│   │   └── user.py            # Pydantic request / response models
│   ├── services/
│   │   └── user_service.py     # Business logic
│   └── main.py                 # FastAPI app entry-point
├── tests/
│   └── test_users.py          # Smoke tests
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env                         # Environment variables
├── .gitignore
├── pyproject.toml
└── README.md
```

| Folder          | Purpose                                                     |
| --------------- | ----------------------------------------------------------- |
| `app/api/`      | HTTP route definitions, organised by API version.           |
| `app/core/`     | App-wide configuration (`Settings`) and security utilities. |
| `app/schemas/`  | Pydantic models for request / response validation.          |
| `app/services/` | Business-logic layer — keeps route handlers thin.           |
| `app/models/`   | ORM model classes mapped to database tables.                |
| `app/db/`       | Database engine, session management, and ORM base class.    |
| `tests/`        | Automated test suite.                                       |

## Database

This project is pre-configured for **Postgresql**.

- Connection URL is set via the `DATABASE_URL` environment variable (see `.env`).
- A `get_session()` dependency is provided in `app/db/session.py` — inject it into any route with `Depends(get_session)`.

## ORM

Models use **SQLAlchemy** and inherit from the shared `Base` in `app/db/base.py`.

To add a new model:

1. Create a file in `app/models/` (e.g. `item.py`).
2. Import `Base` from `app.db.base`.
3. Import the model in `app/models/__init__.py` so migrations can discover it.

## Docker

```bash
# Build and start
docker compose up --build

# Or run directly
docker build -t app .
docker run -p 8000:8000 --env-file .env app
```

## Testing

```bash
uv run pytest
```

Tests live in the `tests/` directory. Every async test needs the `@pytest.mark.asyncio` decorator.

## Linting & Formatting

```bash
uv run ruff check .     # Lint
uv run ruff format .    # Format
```

## Environment Variables

| Variable       | Default                 | Description                        |
| -------------- | ----------------------- | ---------------------------------- |
| `APP_NAME`     | `"task-management-api"` | Display name used in OpenAPI docs. |
| `DEBUG`        | `true`                  | Enable debug mode.                 |
| `DATABASE_URL` | _(see .env)_            | Database connection string.        |

## Tech Stack

- **FastAPI** — async web framework
- **Pydantic** — data validation
- **SQLAlchemy** — ORM
- **Postgresql** — database
- **pytest** + **httpx** — testing
- **Ruff** — linter & formatter
- **Docker** — containerisation
