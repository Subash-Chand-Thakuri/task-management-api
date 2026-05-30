# `app/` — Application Package

This is the root Python package for the FastAPI application.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Makes `app` a Python package. |
| `main.py` | Application entry-point — creates the `FastAPI` instance, mounts routers, and defines the `/health` endpoint. |

## Sub-packages

| Folder | Description |
|--------|-------------|
| `api/` | HTTP route definitions organised by version. |
| `core/` | App-wide configuration and security utilities. |
| `models/` | ORM / database model classes *(present only when an ORM is selected)*. |
| `schemas/` | Pydantic models used for request / response validation. |
| `services/` | Business-logic layer — keeps routes thin. |
| `db/` | Database engine, session, and base model setup *(present only when a database or ORM is selected)*. |
