# `app/core/` — Configuration & Security

App-wide settings and security utilities that are used across the entire application.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package marker. |
| `config.py` | `Settings` class (powered by **pydantic-settings**). Reads values from environment variables and `.env`. Import as `from app.core.config import settings`. |
| `security.py` | OAuth2 scheme definition and any future auth helpers (JWT encoding, password hashing, etc.). |
