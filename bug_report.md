# Bug Report - Todo App

This document outlines the 4 bugs identified in the codebase, their root causes, and how they were fixed.

---

## Bug 1: Tokens Expire Immediately After Login

**File:** `app/auth.py`
**Lines:** ~31

### What the bug was and why it caused incorrect behavior
In the `create_access_token` function, the token expiration time was being calculated by **subtracting** `timedelta` from the current time. This placed the token's expiration date in the past. As a result, the token was instantly invalid the moment it was created, causing all authenticated endpoints to return a `401 Unauthorized` ("Could not validate credentials") error.

### How it was fixed
Changed the subtraction (`-`) to addition (`+`) so that the token correctly expires in the future.
```diff
- expire = datetime.now(timezone.utc) - timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
+ expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
```

---

## Bug 2: Updating a Todo Wipes Unchanged Fields

**File:** `app/main.py`
**Lines:** ~92

### What the bug was and why it caused incorrect behavior
In the `update_todo` endpoint (`PUT /todos/{id}`), the code iterated over `todo_in.model_dump().items()`. Since `model_dump()` by default returns all fields in the schema (including those that were not provided in the request body and defaulted to `None`), it blindly applied `None` to the database object for omitted fields. This wiped out existing data (like description, deadline, or priority) when the user only intended to update a single field like the title.

### How it was fixed
Passed `exclude_unset=True` into `model_dump()` so that only the fields explicitly provided by the user in the request body are dumped and applied.
```diff
- for field, value in todo_in.model_dump().items():
+ for field, value in todo_in.model_dump(exclude_unset=True).items():
```

---

## Bug 3: Any User Can See Every Todo in the System

**File:** `app/main.py`
**Lines:** ~72

### What the bug was and why it caused incorrect behavior
In the `list_todos` endpoint (`GET /todos`), the database query simply returned `db.query(models.Todo).all()`. This queried the entire `todos` table without applying any ownership filter, causing the endpoint to leak every user's tasks to anyone who was authenticated.

### How it was fixed
Added a `.filter()` condition to the query to restrict the results to only the rows where `owner_id` matches the authenticated `current_user.id`.
```diff
- return db.query(models.Todo).all()
+ return db.query(models.Todo).filter(models.Todo.owner_id == current_user.id).all()
```

---

## Bug 4: Database Connections Leak When Requests Fail

**File:** `app/database.py`
**Lines:** ~14-16

### What the bug was and why it caused incorrect behavior
In the FastAPI dependency generator `get_db()`, the session was yielded to the endpoint, followed by `db.close()`. However, if an exception occurred in the endpoint (e.g., raising an `HTTPException`), the code flow would break out before reaching `db.close()`. This caused database connections to never be released back to the connection pool upon errors, eventually exhausting the pool and causing the app to hang.

### How it was fixed
Wrapped the `yield db` statement in a `try` block, and placed `db.close()` inside a `finally` block. This guarantees that the connection is closed and returned to the pool regardless of whether an exception is raised or not.
```diff
  def get_db():
      db = SessionLocal()
-     yield db
-     db.close()
+     try:
+         yield db
+     finally:
+         db.close()
```
