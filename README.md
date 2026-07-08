# Simple Todo App (FastAPI)

Minimal todo API with JWT authentication. Each todo has a title, description, deadline, and priority. Users only see their own todos.

## Stack

- FastAPI + SQLAlchemy (SQLite)
- JWT auth (python-jose) + bcrypt password hashing (passlib)
- Docker / docker-compose

## Run with Docker

```bash
docker compose up --build
```

App runs at `http://localhost:8000`. SQLite file persists in the `todo-data` volume.

Optional: set a real secret via env var before starting:

```bash
SECRET_KEY=some-long-random-string docker compose up --build
```

## Run without Docker

```bash
python -m venv .venv
.venv/Scripts/activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API

Interactive docs at `http://localhost:8000/docs`.

### Auth

| Method | Path | Body | Description |
|---|---|---|---|
| POST | `/auth/register` | JSON `{"username", "password"}` | Create a user |
| POST | `/auth/login` | form-urlencoded `username`, `password` | Returns `{"access_token", "token_type"}` |

`/auth/login` must be sent as `x-www-form-urlencoded`, not JSON (OAuth2 password flow requirement).

All `/todos` endpoints require header `Authorization: Bearer <access_token>`.

### Todos

| Method | Path | Body | Description |
|---|---|---|---|
| POST | `/todos` | `{"title", "description", "deadline", "priority"}` | Create a todo |
| GET | `/todos` | - | List your todos |
| GET | `/todos/{id}` | - | Get one todo |
| PUT | `/todos/{id}` | any subset of the create fields | Edit a todo |
| DELETE | `/todos/{id}` | - | Delete a todo |

Field notes:
- `title`: string, required
- `description`: string, optional
- `deadline`: ISO 8601 datetime string, optional, e.g. `2026-07-10T18:30:00`
- `priority`: one of `low`, `medium`, `high`, default `medium`

## Example requests (curl)

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "pass123"}'

# Login (form-urlencoded, NOT json)
curl -X POST http://localhost:8000/auth/login \
  -d "username=alice&password=pass123"
# -> {"access_token": "<TOKEN>", "token_type": "bearer"}

# Create a todo
curl -X POST http://localhost:8000/todos \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "description": "2% milk", "deadline": "2026-07-10T18:30:00", "priority": "high"}'

# List todos
curl http://localhost:8000/todos -H "Authorization: Bearer <TOKEN>"

# Edit a todo (any subset of fields)
curl -X PUT http://localhost:8000/todos/1 \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"priority": "low"}'

# Delete a todo
curl -X DELETE http://localhost:8000/todos/1 -H "Authorization: Bearer <TOKEN>"
```

## Postman quick setup

1. **Register**: POST `http://localhost:8000/auth/register`, Body → `raw` / JSON → `{"username": "alice", "password": "pass123"}`
2. **Login**: POST `http://localhost:8000/auth/login`, Body → `x-www-form-urlencoded` → keys `username`, `password`. Copy `access_token` from response.
3. **Todos**: any `/todos` request → Authorization tab → type `Bearer Token` → paste token (or add header `Authorization: Bearer <token>` manually).
