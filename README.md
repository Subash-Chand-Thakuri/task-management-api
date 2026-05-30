# Task Management System API

Role-based task management REST API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. Supports JWT authentication and three roles: `ADMIN`, `MANAGER`, and `USER`.

**Base URL:** `http://127.0.0.1:8000`  
**API prefix:** `/v1`  
**Interactive docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Why `uv` and `pyproject.toml`?

This project uses **`pyproject.toml`** as the single source of truth for the Python package and **`uv`** to install dependencies and run commands.

### What `pyproject.toml` does

`pyproject.toml` is the standard modern Python project file (PEP 621). In this repo it defines:

| Section | Purpose |
|---------|---------|
| `[project]` | Project name, version, Python version (`>=3.10`), and **dependencies** (FastAPI, SQLAlchemy, Alembic, pytest, etc.) |
| `[project.scripts]` | CLI entry points — e.g. `uv run seed-db` runs the database seed script |

Instead of a separate `requirements.txt`, everything lives in one file that tools and IDEs understand. When you add a dependency, you update `pyproject.toml` (and commit `uv.lock` for reproducible installs).

### What `uv` does

[uv](https://docs.astral.sh/uv/) is a fast Python package and project manager (by Astral, same team as Ruff). It replaces the usual combo of `pip`, `venv`, and `pip-tools` with one tool.

| Command | What it does |
|---------|----------------|
| `uv sync` | Creates/updates `.venv` and installs exact versions from `uv.lock` |
| `uv run <command>` | Runs a command inside the project virtualenv (no manual `source .venv/bin/activate`) |
| `uv add <package>` | Adds a dependency to `pyproject.toml` and updates the lockfile |

**Why we use it here:**

- **Reproducible installs** — `uv.lock` pins versions so dev, CI, and Docker get the same packages.
- **Speed** — dependency resolution and installs are much faster than pip.
- **Simple workflow** — one tool for venv, install, run server, migrations, and tests.
- **No global pollution** — each project keeps its own `.venv`; system Python stays clean.

Example — same project, consistent environment:

```bash
uv sync                              # install dependencies
uv run uvicorn app.main:app --reload # run API
uv run alembic upgrade head          # run migrations
uv run pytest                        # run tests
uv run seed-db                       # run seed script (defined in pyproject.toml)
```

You do **not** need to activate a virtualenv manually; `uv run` handles that.

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended)
- PostgreSQL 15+ (local or Docker)

### 1. Clone and install

```bash
cd task-management-api
uv sync
```

### 2. Configure environment

Copy the example env file and fill in values:

```bash
cp .env.example .env
```

See [Environment Variables](#environment-variables) below.

### 3. Run database migrations

```bash
uv run alembic upgrade head
```

This applies all migrations in `alembic/versions/` and creates `roles`, `users`, and `tasks` tables.

### 4. Start the server

```bash
uv run uvicorn app.main:app --reload
```

On startup, if `SEED_ON_STARTUP=true`, the app seeds roles (`ADMIN`, `MANAGER`, `USER`) and a default admin user.

### 5. Verify

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

Open Swagger UI at `/docs` or import the Postman collection from `docs/postman/`.

### Docker (optional)

```bash
docker compose up --build
```

API: `http://localhost:8000` · Postgres: `localhost:5435`

Run migrations inside the container if needed:

```bash
docker compose exec task-management-api uv run alembic upgrade head
```

### Deploying to a new environment

1. Create an empty PostgreSQL database.
2. Set `DATABASE_URL` (and other env vars) in that environment.
3. Run `uv run alembic upgrade head`.
4. Start the app (seed runs if `SEED_ON_STARTUP=true`).

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | Async Postgres URL, e.g. `postgresql+asyncpg://user:pass@localhost:5432/dbname` |
| `JWT_SECRET_KEY` | No | `jwt_secret_key` | Secret for signing JWT access tokens. **Change in production.** |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Token lifetime in minutes |
| `ADMIN_EMAIL` | No | `admin@mailsac.com` | Seed admin email |
| `ADMIN_PASSWORD` | No | `Password111!` | Seed admin password |
| `ADMIN_NAME` | No | `System Admin` | Seed admin display name |
| `SEED_ON_STARTUP` | No | `true` | Seed roles + admin on app startup |
| `DEBUG` | No | `true` | SQLAlchemy echo / debug mode |
| `APP_NAME` | No | `task-management-api` | Application name |

Docker-only (used in `docker-compose.yml`):

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | Postgres username |
| `POSTGRES_PASSWORD` | Postgres password |
| `POSTGRES_DB` | Postgres database name |

Example `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/task_management
JWT_SECRET_KEY=change-me-in-production
SEED_ON_STARTUP=true
```

---

## API Usage Guide

### Authentication

1. **Login** — `POST /v1/auth/login`

```json
{
  "email": "admin@mailsac.com",
  "password": "Password111!"
}
```

Response:

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "<jwt>",
    "token_type": "bearer"
  }
}
```

2. **Protected routes** — send the token on every request:

```http
Authorization: Bearer <access_token>
```

3. **Public routes** — no token required:
   - `POST /v1/users/` (signup)
   - `GET /v1/roles/`, `GET /v1/roles/{id}`
   - `POST /v1/auth/login`

### Response envelope

All endpoints return a consistent shape:

```json
{
  "success": true,
  "message": "OK",
  "data": { },
  "errors": null
}
```

Paginated lists wrap items like this:

```json
{
  "success": true,
  "message": "OK",
  "data": {
    "items": [ ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 25,
      "total_pages": 3
    }
  }
}
```

### Endpoints summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Health check |
| POST | `/v1/auth/login` | — | Login, get JWT |
| POST | `/v1/users/` | — | Sign up (defaults to USER role) |
| GET | `/v1/users/me` | Any | Current user profile |
| GET | `/v1/users/` | Any | List users (paginated, role-filtered) |
| GET | `/v1/users/{id}` | Manager+ | Get user by ID |
| PUT | `/v1/users/{id}` | Manager+ | Update user |
| DELETE | `/v1/users/{id}` | Admin | Delete user |
| GET | `/v1/roles/` | — | List roles |
| GET | `/v1/roles/{id}` | — | Get role |
| POST | `/v1/roles/` | Admin | Create role |
| PUT | `/v1/roles/{id}` | Admin | Update role |
| DELETE | `/v1/roles/{id}` | Admin | Delete role |
| GET | `/v1/tasks/` | Any | List tasks (paginated, role-filtered) |
| POST | `/v1/tasks/` | Manager+ | Create task |
| GET | `/v1/tasks/{id}` | Any | Get task (access-checked) |
| PUT | `/v1/tasks/{id}` | Any | Update task (field rules by role) |
| DELETE | `/v1/tasks/{id}` | Admin | Delete task |

### Query parameters (list endpoints)

**Tasks** — `GET /v1/tasks/`

| Param | Default | Description |
|-------|---------|-------------|
| `page` | `1` | Page number (≥ 1) |
| `page_size` | `10` | Items per page (≥ 1) |
| `sort` | `created_at` | `id`, `title`, `status`, `due_date`, `created_at`, `updated_at` |
| `order` | `asc` | `asc` or `desc` |
| `search` | — | Filter by title or description |

**Users** — `GET /v1/users/`

| Param | Default | Description |
|-------|---------|-------------|
| `page` | `1` | Page number |
| `page_size` | `10` | Items per page |
| `sort` | `id` | `id`, `email`, `name`, `is_active`, `role_id`, `created_at`, `updated_at` |
| `order` | `asc` | `asc` or `desc` |
| `role_id` | — | Filter by role |
| `is_active` | — | Filter by active status |
| `search` | — | Filter by name or email |

Example:

```http
GET /v1/tasks/?page=1&page_size=10&sort=created_at&order=desc&search=bug
Authorization: Bearer <token>
```

### RBAC rules

**Tasks**

| Role | List / get | Create | Update | Delete |
|------|------------|--------|--------|--------|
| Admin | All tasks | Yes | All fields | Yes |
| Manager | Assigned to or created by them | Yes | `status` only | No |
| User | Assigned to them | No | `status` only | No |

- Completed tasks **cannot** be reverted to `PENDING`.
- Managers assign users via `assigned_to` on **create**.

**Users**

| Role | List | Get / update others | Delete |
|------|------|---------------------|--------|
| Admin | All users | Yes | Yes |
| Manager | Self + USER-role accounts | Yes | No |
| User | Self only | No (except `/me`) | No |

---

## Architecture

```
Client (HTTP)
    │
    ▼
app/api/v1/          Route handlers, query params, auth deps
    │
    ▼
app/services/        Business logic, RBAC, pagination
    │
    ▼
app/models/          SQLAlchemy ORM
    │
    ▼
PostgreSQL
```

| Layer | Responsibility |
|-------|----------------|
| **API** (`app/api/`) | HTTP routing, request validation (Pydantic), auth dependencies |
| **Services** (`app/services/`) | RBAC filtering, pagination, business rules |
| **Schemas** (`app/schemas/`) | Request/response models |
| **Models** (`app/models/`) | Database tables |
| **Core** (`app/core/`) | Config, JWT, exceptions, logging |
| **DB** (`app/db/`) | Engine, session, seed |
| **Utils** (`app/utils/`) | Standard responses, validators |

Auth flow:

1. `POST /auth/login` validates credentials and returns JWT (`sub` = user email).
2. Protected routes use `HTTPBearer` + `get_auth_context` to load user and role from DB.
3. Role checks via `RequireAdmin`, `RequireManagerOrAdmin`, or `RequireAnyRole`.

---

## Database

See **[docs/DATABASE.md](docs/DATABASE.md)** for ERD, table descriptions, and migration notes.

Migrations live in `alembic/versions/` and should be committed to git.

---

## API Testing

| Option | Location |
|--------|----------|
| **Swagger UI** | `http://127.0.0.1:8000/docs` |
| **ReDoc** | `http://127.0.0.1:8000/redoc` |
| **Swagger testing PDF** | [docs/SWAGGER.md](docs/SWAGGER.md) → [PDF report](docs/assets/task-management-api%20-%20Swagger%20UI.pdf) |
| **Postman collection** | [docs/postman/Task-Management-API.postman_collection.json](docs/postman/Task-Management-API.postman_collection.json) |

Import the Postman collection, set the `baseUrl` variable, run **Auth → Login**, then use other requests (token is saved automatically).

---

## Assumptions and Limitations

- **Single-tenant** — no organization/workspace model; all users share one task pool.
- **JWT only** — no refresh tokens; clients re-login when the token expires.
- **Role stored by ID** — users reference `roles.id`; role names are seeded, not created at runtime in normal use.
- **No email verification** — signup is open; production should add verification or restrict signup.
- **No task comments, attachments, or audit log** — out of scope.
- **Soft delete not implemented** — deletes are permanent.
- **Pagination** — no cursor-based pagination; offset/limit only.
- **Search** — simple `ILIKE` on text fields, not full-text search.
- **Manager task updates** — non-admins can only change `status` on update (assignment happens at create time).
- **Default secrets** — change `JWT_SECRET_KEY` and admin password before production.

---

## Development

```bash
# Tests
uv run pytest

# Lint / format
uv run ruff check .
uv run ruff format .

# New migration (after model changes)
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head

# Manual seed
uv run seed-db
```

## Tech Stack

FastAPI · Pydantic · SQLAlchemy (async) · Alembic · PostgreSQL · JWT (python-jose) · bcrypt · pytest · httpx · Ruff · Docker
