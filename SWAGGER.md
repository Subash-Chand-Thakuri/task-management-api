# Swagger API testing

Proof of manual API testing via Swagger UI.

**Live docs:** http://127.0.0.1:8000/docs

---

## Testing report (PDF)

**[Open Swagger UI testing report (PDF)](docs/assets/task-management-api%20-%20Swagger%20UI.pdf)**

File location: `docs/assets/task-management-api - Swagger UI.pdf`

---

## What the PDF covers

| #   | Test          | Endpoint                      |
| --- | ------------- | ----------------------------- |
| 1   | Login         | `POST /v1/auth/login`         |
| 2   | Current user  | `GET /v1/users/me`            |
| 3   | List tasks    | `GET /v1/tasks/`              |
| 4   | Create task   | `POST /v1/tasks/`             |
| 5   | Update status | `PUT /v1/tasks/{id}`          |
| 6   | RBAC (403)    | e.g. delete task as non-admin |

Use **Authorize** in Swagger with: `Bearer <token>` from login.
