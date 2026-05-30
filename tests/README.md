# `tests/` — Test Suite

Automated tests for the application, using **pytest** and **httpx**.

## Files

| File | Description |
|------|-------------|
| `__init__.py` | Package marker. |
| `test_users.py` | Smoke test — calls `GET /health` and asserts a 200 response. |

## Running tests

```bash
uv run pytest
```

## Tips

- Name test files `test_<module>.py` so pytest discovers them automatically.
- Use `@pytest.mark.asyncio` on every `async def test_...` function.
- Add a `conftest.py` for shared fixtures (app client, test DB, etc.).
