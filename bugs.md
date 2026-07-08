# Bug Hunt — Todo App

This document lists all bugs in the codebase for you to find and fix. Each entry describes the symptom you'll observe, a hint to guide your search, and the fix.

---

## Bug 1 — Tokens Expire Immediately After Login

**Difficulty:** Easy  
**File:** `app/auth.py`

### Symptom
You can register and log in successfully, but every subsequent request that requires authentication returns:
```json
{"detail": "Could not validate credentials"}
```
The token you received is immediately invalid.

### Hint
Look at the `create_access_token` function. It calculates an expiry timestamp for the JWT. Think about whether the expiry should be in the future or the past.

### Bug
```python
# Wrong — subtracts the duration, placing expiry in the past
expire = datetime.now(timezone.utc) - timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
```

### Fix
```python
# Correct — adds the duration so the token expires in the future
expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
```

---

## Bug 2 — Updating a Todo Wipes Fields You Didn't Touch

**Difficulty:** Easy  
**File:** `app/main.py`

### Symptom
You send a PUT request to `/todos/{id}` with only `{"title": "New Title"}`. Instead of just updating the title, all other fields (`description`, `deadline`, `priority`) are reset to `null` / their defaults.

### Hint
Look at the `update_todo` endpoint. It iterates over the fields from `todo_in` and applies them to the database object. Consider: when you don't include a field in the request body, what value does it have in the parsed model, and are those values being applied?

### Bug
```python
# Wrong — dumps ALL fields including ones the client never sent (they default to None)
for field, value in todo_in.model_dump().items():
    setattr(todo, field, value)
```

### Fix
```python
# Correct — only iterates fields the client actually provided
for field, value in todo_in.model_dump(exclude_unset=True).items():
    setattr(todo, field, value)
```

---

## Bug 3 — Any User Can See Every Todo in the System

**Difficulty:** Medium  
**File:** `app/main.py`

### Symptom
The `GET /todos` endpoint returns todos from **all users**, not just the authenticated user's own todos. User A can see User B's tasks.

### Hint
Look at the `list_todos` endpoint. Compare how it queries the database versus how the `get_todo` (single item) endpoint does it. Something is missing from the query that restricts results to the current user.

### Bug
```python
# Wrong — returns every todo row with no ownership filter
return db.query(models.Todo).all()
```

### Fix
```python
# Correct — filters to only the current user's todos
return db.query(models.Todo).filter(models.Todo.owner_id == current_user.id).all()
```

---

## Bug 4 — Database Connections Leak When Requests Fail

**Difficulty:** Medium  
**File:** `app/database.py`

### Symptom
Under normal usage the app works fine, but when requests fail with an error (e.g., a `404` or `422`), the database connection is never returned to the pool. Under load or after many errors, the app starts hanging or refusing new connections.

### Hint
Look at the `get_db` generator function that provides database sessions to endpoints. FastAPI dependency generators should clean up resources even when the request raises an exception. What Python construct guarantees code runs regardless of whether an exception occurred?

### Bug
```python
# Wrong — db.close() is never called if an exception is raised before it
def get_db():
    db = SessionLocal()
    yield db
    db.close()
```

### Fix
```python
# Correct — finally block ensures the connection is always released
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
