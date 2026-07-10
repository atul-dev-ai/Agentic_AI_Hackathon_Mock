# 📝 Simple Todo API (FastAPI)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

A minimal, lightning-fast Todo REST API built with **FastAPI**. It features secure JWT authentication, password hashing, and user-specific task management where each user can only access their own todos.

---

## ✨ Features

- **User Authentication:** Secure signup and login using JWT (`python-jose`) and `bcrypt` password hashing.
- **Task Management:** Create, read, update, and delete (CRUD) your own todo items.
- **Task Attributes:** Manage your tasks with titles, descriptions, deadlines, and priority levels (Low, Medium, High).
- **Data Isolation:** Strict ownership validation ensures you only see what belongs to you.
- **Interactive Docs:** Auto-generated Swagger UI for easy API testing.

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Database:** SQLAlchemy + SQLite
- **Auth:** OAuth2 with Password Flow & JWT Bearer
- **Deployment:** Docker & Docker Compose

---

## 🚀 Getting Started

You can run this project with or without Docker.

### 🐳 Run with Docker (Recommended)

Simply spin up the containers:
```bash
docker compose up --build
```
> The API will be available at `http://localhost:8000`. 
> Data is persisted automatically in a Docker volume.

### 💻 Run Locally (Without Docker)

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows:
   .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 📖 API Documentation

Once the server is running, visit **[http://localhost:8000/docs](http://localhost:8000/docs)** to view the interactive Swagger UI and test the endpoints directly from your browser!

### 🔐 Authentication

| Method | Endpoint | Description | Body Requirements |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Create a new user | JSON: `{"username", "password"}` |
| `POST` | `/auth/login` | Log in & get JWT | `x-www-form-urlencoded`: `username`, `password` |

> ⚠️ **Note:** The `/auth/login` endpoint strictly requires `x-www-form-urlencoded` format.

### 📋 Todos

*Requires header: `Authorization: Bearer <access_token>`*

| Method | Endpoint | Description | Body Requirements |
| :--- | :--- | :--- | :--- |
| `POST` | `/todos` | Create a new todo | JSON: `title`*, `description`, `deadline`, `priority` |
| `GET` | `/todos` | List all your todos | - |
| `GET` | `/todos/{id}` | Get a specific todo | - |
| `PUT` | `/todos/{id}` | Update a todo | JSON (Any subset of create fields) |
| `DELETE` | `/todos/{id}` | Delete a todo | - |

---

## 🧪 Testing with cURL

Here are some quick commands to get you started:

<details>
<summary><b>Show cURL Commands</b></summary>

**1. Register**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "pass123"}'
```

**2. Login**
```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=alice&password=pass123"
```
*(Copy the `access_token` from the response)*

**3. Create a Todo**
```bash
curl -X POST http://localhost:8000/todos \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "priority": "high"}'
```

**4. View Todos**
```bash
curl http://localhost:8000/todos -H "Authorization: Bearer <YOUR_TOKEN>"
```

</details>
